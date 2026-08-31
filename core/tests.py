from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Inquiry, Certificate


class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.tobacco = Product.objects.create(
            name="Raw Tobacco Leaf",
            slug="raw-tobacco-leaf",
            origin="India",
            short_description="Export-grade raw tobacco leaves.",
            overview="Detailed tobacco overview.",
            is_active=True,
            display_order=1
        )
        self.moringa = Product.objects.create(
            name="Moringa Leaf Powder",
            slug="moringa-leaf-powder",
            botanical_name="Moringa oleifera",
            origin="India",
            short_description="Pure moringa leaf powder.",
            overview="Detailed moringa overview.",
            is_active=True,
            display_order=2
        )

    def test_public_pages_status_code(self):
        urls = [
            reverse('core:home'),
            reverse('core:about'),
            reverse('core:product_list'),
            reverse('core:product_detail', args=['raw-tobacco-leaf']),
            reverse('core:product_detail', args=['moringa-leaf-powder']),
            reverse('core:our_approach'),
            reverse('core:certificates'),
            reverse('core:contact'),
            reverse('core:sitemap_xml'),
            reverse('core:robots_txt'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed on URL: {url}")

    def test_inquiry_submission_success(self):
        payload = {
            'name': 'Ahmed Al-Mansoor',
            'email': 'procurement@gulfdistributors.ae',
            'company_name': 'Gulf Commodity Trading LLC',
            'mobile_number': '+971 50 123 4567',
            'country': 'United Arab Emirates',
            'product': 'Raw Tobacco Leaf',
            'product_details': 'Requesting commercial FOB quote for 2 FCL (40ft containers), unmanufactured leaf.',
            'remarks': 'Required delivery timeline Q4.',
            'website_url': '',  # Honeypot empty
        }
        response = self.client.post(reverse('core:submit_inquiry'), data=payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))

        # Verify record exists in Django database
        inquiry = Inquiry.objects.get(email='procurement@gulfdistributors.ae')
        self.assertEqual(inquiry.name, 'Ahmed Al-Mansoor')
        self.assertEqual(inquiry.company_name, 'Gulf Commodity Trading LLC')
        self.assertEqual(inquiry.product, 'Raw Tobacco Leaf')
        self.assertEqual(inquiry.status, Inquiry.STATUS_NEW)

    def test_inquiry_honeypot_spam_rejection(self):
        payload = {
            'name': 'Spam Bot',
            'email': 'bot@spam.com',
            'mobile_number': '+1 555 000 0000',
            'country': 'USA',
            'product': 'Raw Tobacco Leaf',
            'website_url': 'http://automated-spam-site.com',  # Filled honeypot
        }
        response = self.client.post(reverse('core:submit_inquiry'), data=payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Inquiry.objects.filter(email='bot@spam.com').count(), 0)

    def test_certificates_page_coming_soon_display(self):
        response = self.client.get(reverse('core:certificates'))
        self.assertContains(response, "COMING SOON")
        self.assertContains(response, "Quality & Compliance")

    def test_product_preselection_on_contact_page(self):
        response_tobacco = self.client.get(reverse('core:contact') + '?product=raw-tobacco-leaf')
        self.assertEqual(response_tobacco.status_code, 200)
        self.assertContains(response_tobacco, 'Selected Commodity: <strong>Raw Tobacco Leaf</strong>')

        response_moringa = self.client.get(reverse('core:contact') + '?product=moringa-leaf-powder')
        self.assertEqual(response_moringa.status_code, 200)
        self.assertContains(response_moringa, 'Selected Commodity: <strong>Moringa Leaf Powder</strong>')

    def test_product_detail_has_no_full_form(self):
        response = self.client.get(reverse('core:product_detail', args=['raw-tobacco-leaf']))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<form action="/submit-inquiry/"')
        self.assertContains(response, 'Inquire Now')
        self.assertContains(response, '/contact/?product=raw-tobacco-leaf')


class DomainConfigurationTestCase(TestCase):
    """
    Validates that the new production domains (vedop.fun, www.vedop.fun)
    and existing Render domain (kailashglobalimpex.onrender.com) are properly accepted.
    """

    def test_production_hosts_accepted(self):
        hosts = [
            'vedop.fun',
            'www.vedop.fun',
            'kailashglobalimpex.onrender.com',
            'kailashglobalimpex.com',
            'www.kailashglobalimpex.com',
            'localhost',
            '127.0.0.1',
        ]
        for host in hosts:
            response = self.client.get('/', HTTP_HOST=host)
            self.assertEqual(response.status_code, 200, f"Host '{host}' was rejected with status {response.status_code}")

    def test_csrf_trusted_origins_configuration(self):
        from django.conf import settings
        required_origins = [
            'https://vedop.fun',
            'https://www.vedop.fun',
            'https://kailashglobalimpex.onrender.com',
        ]
        for origin in required_origins:
            self.assertIn(origin, settings.CSRF_TRUSTED_ORIGINS, f"Origin '{origin}' is missing from CSRF_TRUSTED_ORIGINS")

    def test_dynamic_site_domain_context_processor(self):
        response = self.client.get('/', HTTP_HOST='vedop.fun', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://vedop.fun')

    def test_post_with_csrf_on_custom_domain(self):
        csrf_client = Client(enforce_csrf_checks=True)
        payload = {
            'name': 'Ved Patel',
            'email': 'ved@example.com',
            'company_name': 'Global Trading',
            'mobile_number': '+91 9999999999',
            'country': 'India',
            'product': 'Raw Tobacco Leaf',
            'product_details': 'Testing inquiry on custom domain.',
            'remarks': 'Testing',
            'website_url': '',
        }
        get_resp = csrf_client.get(reverse('core:contact'), HTTP_HOST='vedop.fun', secure=True)
        csrf_token = get_resp.cookies['csrftoken'].value
        response = csrf_client.post(
            reverse('core:submit_inquiry'),
            data=payload,
            HTTP_HOST='vedop.fun',
            HTTP_ORIGIN='https://vedop.fun',
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            secure=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))


import xml.etree.ElementTree as ET


class SitemapAndRobotsTestCase(TestCase):
    """
    Tests ensuring sitemap.xml and robots.txt strictly satisfy
    Googlebot and Google Search Console requirements.
    """

    def setUp(self):
        self.client = Client()
        self.tobacco = Product.objects.create(
            name="Raw Tobacco Leaf",
            slug="raw-tobacco-leaf",
            origin="India",
            short_description="Export-grade raw tobacco leaves.",
            overview="Detailed tobacco overview.",
            is_active=True,
            display_order=1
        )
        self.moringa = Product.objects.create(
            name="Moringa Leaf Powder",
            slug="moringa-leaf-powder",
            botanical_name="Moringa oleifera",
            origin="India",
            short_description="Pure moringa leaf powder.",
            overview="Detailed moringa overview.",
            is_active=True,
            display_order=2
        )
        # Create an inactive product to test exclusion
        self.inactive_product = Product.objects.create(
            name="Inactive Test Product",
            slug="inactive-test-product",
            origin="India",
            short_description="Hidden product.",
            overview="Hidden overview.",
            is_active=False,
            display_order=99
        )

    def test_sitemap_get_success_and_headers(self):
        response = self.client.get('/sitemap.xml', HTTP_HOST='vedop.fun')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/xml', response['Content-Type'])

    def test_sitemap_head_request(self):
        response = self.client.head('/sitemap.xml', HTTP_HOST='vedop.fun')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/xml', response['Content-Type'])

    def test_sitemap_googlebot_user_agent(self):
        response = self.client.get(
            '/sitemap.xml',
            HTTP_HOST='vedop.fun',
            HTTP_USER_AGENT='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        )
        self.assertEqual(response.status_code, 200)

    def test_sitemap_xml_validity_and_urls(self):
        response = self.client.get('/sitemap.xml', HTTP_HOST='vedop.fun')
        self.assertEqual(response.status_code, 200)

        # Parse XML to guarantee strict conformance
        root = ET.fromstring(response.content)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        loc_elements = root.findall('.//sm:loc', ns)
        locs = [el.text for el in loc_elements]

        # 8 expected canonical public URLs
        expected_urls = [
            'https://vedop.fun/',
            'https://vedop.fun/about/',
            'https://vedop.fun/products/',
            'https://vedop.fun/our-approach/',
            'https://vedop.fun/certificates/',
            'https://vedop.fun/contact/',
            'https://vedop.fun/products/raw-tobacco-leaf/',
            'https://vedop.fun/products/moringa-leaf-powder/',
        ]

        self.assertEqual(len(locs), 8)
        for expected in expected_urls:
            self.assertIn(expected, locs, f"Missing URL in sitemap: {expected}")

        # Inactive product must NOT be in sitemap
        self.assertNotIn('https://vedop.fun/products/inactive-test-product/', locs)

        # Private / admin / inquiry POST URLs must NOT be in sitemap
        for private in ['/admin/', '/admin-panel/', '/submit-inquiry/']:
            self.assertFalse(any(private in loc for loc in locs), f"Private URL found in sitemap: {private}")

    def test_robots_txt_content_and_sitemap_reference(self):
        response = self.client.get('/robots.txt', HTTP_HOST='vedop.fun')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/plain', response['Content-Type'])
        content = response.content.decode('utf-8')
        self.assertIn('User-agent: *', content)
        self.assertIn('Allow: /', content)
        self.assertIn('Disallow: /admin/', content)
        self.assertIn('Disallow: /admin-panel/', content)
        self.assertIn('Sitemap: https://vedop.fun/sitemap.xml', content)

    def test_robots_txt_head_request(self):
        response = self.client.head('/robots.txt', HTTP_HOST='vedop.fun')
        self.assertEqual(response.status_code, 200)

