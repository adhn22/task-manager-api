from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterTests(APITestCase):
    def setUp(self):
        self.url = '/api/auth/register/'
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_register_password_mismatch(self):
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPass!'
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        User.objects.create_user(username='testuser', password='pass1234')
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        data = self.valid_data.copy()
        data['password'] = '123'
        data['password2'] = '123'
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.url = '/api/auth/login/'
        self.user = User.objects.create_user(
            username='testuser', password='StrongPass123!'
        )

    def test_login_success(self):
        data = {'username': 'testuser', 'password': 'StrongPass123!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        data = {'username': 'testuser', 'password': 'WrongPass!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        data = {'username': 'nouser', 'password': 'pass1234'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileTests(APITestCase):
    def setUp(self):
        self.url = '/api/auth/profile/'
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='StrongPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_profile(self):
        data = {'email': 'new@example.com', 'first_name': 'Test'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')

    def test_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.url = '/api/auth/change-password/'
        self.user = User.objects.create_user(
            username='testuser', password='OldPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        data = {'old_password': 'OldPass123!', 'new_password': 'NewPass456!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass456!'))

    def test_change_password_wrong_old(self):
        data = {'old_password': 'WrongOld!', 'new_password': 'NewPass456!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_weak_new(self):
        data = {'old_password': 'OldPass123!', 'new_password': '123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTests(APITestCase):
    def setUp(self):
        self.url = '/api/auth/logout/'
        self.user = User.objects.create_user(
            username='testuser', password='StrongPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_logout_success(self):
        refresh = RefreshToken.for_user(self.user)
        data = {'refresh': str(refresh)}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_invalid_token(self):
        data = {'refresh': 'invalidtoken'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
