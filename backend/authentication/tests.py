import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import EmployeeProfile


class AuthenticationApiTests(TestCase):
    frontend_origin = 'http://127.0.0.1:5500'

    def setUp(self):
        self.user = User.objects.create_user(
            username='nv01', password='MatKhauBanDau!234',
            first_name='An', last_name='Nguyễn',
        )
        self.profile = EmployeeProfile.objects.create(user=self.user)

    def _csrf_client(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse('api_csrf'), HTTP_ORIGIN=self.frontend_origin)
        self.assertEqual(response.status_code, 200)
        self.assertIn('csrftoken', response.cookies)
        return client, response.cookies['csrftoken'].value

    def test_csrf_endpoint_allows_configured_frontend_origin(self):
        response = self.client.get(reverse('api_csrf'), HTTP_ORIGIN=self.frontend_origin)
        self.assertEqual(response['access-control-allow-origin'], self.frontend_origin)
        self.assertEqual(response['access-control-allow-credentials'], 'true')

    def test_session_requires_authentication(self):
        self.assertEqual(self.client.get(reverse('api_session')).status_code, 401)

    def test_login_rejects_request_without_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse('api_login'),
            data=json.dumps({'username': 'nv01', 'password': 'MatKhauBanDau!234'}),
            content_type='application/json', HTTP_ORIGIN=self.frontend_origin,
        )
        self.assertEqual(response.status_code, 403)

    def test_login_creates_session_and_reports_password_change(self):
        client, csrf_token = self._csrf_client()
        response = client.post(
            reverse('api_login'),
            data=json.dumps({'username': 'nv01', 'password': 'MatKhauBanDau!234'}),
            content_type='application/json', HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.frontend_origin,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['must_change_password'])
        self.assertEqual(response.json()['username'], 'An Nguyễn')

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            reverse('api_login'),
            data=json.dumps({'username': 'nv01', 'password': 'sai-mat-khau'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_change_password_unlocks_account_and_keeps_session(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('api_change_password'),
            data=json.dumps({'new_password': '1', 'confirm_password': '1'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.must_change_password)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('1'))
        self.assertEqual(self.client.get(reverse('api_session')).status_code, 200)

    def test_change_password_rejects_mismatched_confirmation(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('api_change_password'),
            data=json.dumps({'new_password': 'abc', 'confirm_password': 'xyz'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_change_password_rejects_empty_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('api_change_password'),
            data=json.dumps({'new_password': '', 'confirm_password': ''}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_logout_ends_session(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse('api_logout')).status_code, 200)
        self.assertEqual(self.client.get(reverse('api_session')).status_code, 401)
