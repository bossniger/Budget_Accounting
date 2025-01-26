from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTestCase(APITestCase):
    def setUp(self):
        self.register_url = '/api/register/'
        self.token_url = '/api/token/'
        self.token_refresh_url = '/api/token/refresh/'

    def test_user_registration(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Пользователь успешно зарегистрирован')

    def test_registration_password_mismatch(self):
        # Данные с разными паролями
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
            "password_confirm": "password456"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password:", response.data)

    def test_user_login(self):
        # Создаем пользователя для теста
        User.objects.create_user(username="testuser", password="password123")
        # Данные для входа
        data = {
            "username": "testuser",
            "password": "password123"
        }
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        # Неверные данные для входа
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_token_refresh(self):
        # Создаем пользователя и получаем токен
        user = User.objects.create_user(username="testuser", password="password123")
        token_response = self.client.post(self.token_url, {
            "username": "testuser",
            "password": "password123"
        })
        refresh_token = token_response.data["refresh"]

        # Обновляем токен
        response = self.client.post(self.token_refresh_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)