import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Account


class AccountAuthBackendTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Account.objects.create_user(
            email='test.customs@ecc.gov.et',
            username='test_customs',
            first_name='Abebe',
            last_name='Kebede',
            password='TestPassword123',
            role=Account.Role.CUSTOMS
        )

    def test_user_creation_and_properties(self):
        self.assertEqual(self.user.email, 'test.customs@ecc.gov.et')
        self.assertTrue(self.user.check_password('TestPassword123'))
        self.assertEqual(self.user.role, Account.Role.CUSTOMS)
        self.assertTrue(self.user.is_customs)
        self.assertFalse(self.user.is_importer)

    def test_login_and_logout_views(self):
        # 1. Login with valid credentials
        res_login = self.client.post(reverse('login'), {
            'username': 'test.customs@ecc.gov.et',
            'password': 'TestPassword123'
        })
        self.assertEqual(res_login.status_code, 302)  # Redirects to dashboard

        # 2. Access authenticated profile
        res_profile = self.client.get(reverse('profile'))
        self.assertEqual(res_profile.status_code, 200)
        self.assertContains(res_profile, 'Abebe')

        # 3. Logout
        res_logout = self.client.get(reverse('logout'))
        self.assertEqual(res_logout.status_code, 302)

    def test_registration_view(self):
        payload = {
            'first_name': 'Dawit',
            'last_name': 'Tadesse',
            'email': 'dawit@gtmotors-et.com',
            'username': 'dawit_importer',
            'role': Account.Role.IMPORTER,
            'password': 'NewPassword123',
            'confirm_password': 'NewPassword123',
        }
        response = self.client.post(reverse('register'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Account.objects.filter(email='dawit@gtmotors-et.com').exists())

    def test_api_auth_endpoints(self):
        # 1. API Login
        res_api_login = self.client.post(
            reverse('api_login'),
            data=json.dumps({'email': 'test.customs@ecc.gov.et', 'password': 'TestPassword123'}),
            content_type='application/json'
        )
        self.assertEqual(res_api_login.status_code, 200)
        self.assertTrue(res_api_login.json()['success'])

        # 2. API Profile
        res_api_prof = self.client.get(reverse('api_profile'))
        self.assertEqual(res_api_prof.status_code, 200)
        self.assertTrue(res_api_prof.json()['authenticated'])
        self.assertEqual(res_api_prof.json()['user']['role'], Account.Role.CUSTOMS)

        # 3. API Users List
        res_users = self.client.get(reverse('api_users_list'))
        self.assertEqual(res_users.status_code, 200)
        self.assertGreaterEqual(res_users.json()['count'], 1)
