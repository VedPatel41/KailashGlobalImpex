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

    def test_inquiry_delete_authenticated_post(self):
        self.client.login(username='admin_tester', password='TestPassword123!')
        inquiry_id = self.inquiry1.id
        url = reverse('admin_panel:inquiry_delete', args=[inquiry_id])
        
        # Test GET renders confirm_delete page
        get_res = self.client.get(url)
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, "Delete Feedback")
        
        # Test POST permanently deletes from database
        post_res = self.client.post(url)
        self.assertEqual(post_res.status_code, 302)
        self.assertFalse(Inquiry.objects.filter(id=inquiry_id).exists())

    def test_inquiry_delete_ajax(self):
        self.client.login(username='admin_tester', password='TestPassword123!')
        inquiry = Inquiry.objects.create(
            name='Temporary Contact',
            email='temp@contact.com',
            mobile_number='+91 9876543210',
            country='India',
            product='Raw Tobacco Leaf'
        )
        url = reverse('admin_panel:inquiry_delete', args=[inquiry.id])
        res = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('deleted successfully', data['message'])
        self.assertFalse(Inquiry.objects.filter(id=inquiry.id).exists())

    def test_inquiry_delete_unauthenticated_rejected(self):
        url = reverse('admin_panel:inquiry_delete', args=[self.inquiry1.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/admin-panel/login/', res.url)
        self.assertTrue(Inquiry.objects.filter(id=self.inquiry1.id).exists())

    def test_inquiry_delete_non_existent(self):
        self.client.login(username='admin_tester', password='TestPassword123!')
        url = reverse('admin_panel:inquiry_delete', args=[99999])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 404)

    def test_admin_on_custom_domain(self):
        res = self.client.get(reverse('admin_panel:login'), HTTP_HOST='kailashglobalimpex.com', secure=True)
        self.assertEqual(res.status_code, 200)

        django_admin_res = self.client.get('/admin/login/', HTTP_HOST='kailashglobalimpex.com', secure=True)
        self.assertEqual(django_admin_res.status_code, 200)

        csrf_client = Client(enforce_csrf_checks=True)
        get_res = csrf_client.get(reverse('admin_panel:login'), HTTP_HOST='kailashglobalimpex.com', secure=True)
        csrf_token = get_res.cookies['csrftoken'].value
        login_res = csrf_client.post(
            reverse('admin_panel:login'),
            data={
                'username': 'admin_tester',
                'password': 'TestPassword123!',
                'csrfmiddlewaretoken': csrf_token,
            },
            HTTP_HOST='kailashglobalimpex.com',
            HTTP_ORIGIN='https://kailashglobalimpex.com',
            secure=True
        )
        self.assertEqual(login_res.status_code, 302)
        self.assertIn('/admin-panel/', login_res.url)
