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
