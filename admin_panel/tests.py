from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Inquiry, Product, Certificate

User = get_user_model()


class AdminPanelTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin_tester',
            email='admin@kailashglobalimpex.com',
            password='TestPassword123!'
        )
        self.inquiry1 = Inquiry.objects.create(
            name='John Smith',
            email='john@smithtraders.co.uk',
            company_name='Smith Traders Ltd',
            mobile_number='+44 20 7946 0958',
            country='United Kingdom',
            product='Moringa Leaf Powder',
            product_details='500 kg test batch inquiry.',
            status=Inquiry.STATUS_NEW
        )

    def test_anonymous_redirect_to_login(self):
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin-panel/login/', response.url)

    def test_authenticated_dashboard_access(self):
        self.client.login(username='admin_tester', password='TestPassword123!')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enterprise Trade Dashboard")
        self.assertContains(response, "John Smith")

    def test_inquiry_status_ajax_update(self):
        self.client.login(username='admin_tester', password='TestPassword123!')
        url = reverse('admin_panel:update_inquiry_status_ajax', args=[self.inquiry1.id])
        response = self.client.post(url, {'status': Inquiry.STATUS_CONTACTED}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.inquiry1.refresh_from_db()
        self.assertEqual(self.inquiry1.status, Inquiry.STATUS_CONTACTED)

    def test_csv_export(self):
        self.client.login(username='admin_tester', password='TestPassword123!')
        response = self.client.get(reverse('admin_panel:export_inquiries_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="KGI_Inquiries_', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('John Smith', content)
        self.assertIn('Moringa Leaf Powder', content)

    def test_products_management_view(self):
        self.client.login(username='admin_tester', password='TestPassword123!')
        response = self.client.get(reverse('admin_panel:products_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Export Commodities Catalog')

    def test_certificate_management_view(self):
        self.client.login(username='admin_tester', password='TestPassword123!')
        response = self.client.get(reverse('admin_panel:certificates_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compliance Certificates')

    def test_add_product_and_toggle(self):
        self.client.login(username='admin_tester', password='TestPassword123!')
        payload = {
            'name': 'Test Spice Commodity',
            'slug': 'test-spice-commodity',
            'origin': 'India',
            'short_description': 'Test export commodity description.',
            'overview': 'Detailed overview for testing.',
            'is_active': True,
            'display_order': 3,
        }
        res = self.client.post(reverse('admin_panel:product_add'), data=payload)
        self.assertEqual(res.status_code, 302)
        
        # Verify created
        p = Product.objects.get(slug='test-spice-commodity')
        self.assertEqual(p.name, 'Test Spice Commodity')
        self.assertTrue(p.is_active)

        # Toggle inactive
        toggle_res = self.client.get(reverse('admin_panel:product_toggle', args=[p.pk]))
        self.assertEqual(toggle_res.status_code, 302)
        p.refresh_from_db()
        self.assertFalse(p.is_active)
