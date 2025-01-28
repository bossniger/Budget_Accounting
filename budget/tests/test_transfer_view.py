from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from budget.models import Currency, Account


class TransferViewTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user3', password='password123')
        self.client.force_authenticate(user=self.user1)
        self.user2 = User.objects.create_user(username='user4', password='password123')
        self.currency = Currency.objects.create(code='BYN', name='Белорусский рубль', rate_to_base=Decimal(1))
        self.account1 = Account.objects.create(
            user=self.user1, name='Основной счет', account_type='cash', currency=self.currency, balance=Decimal(500)
        )
        self.account2 = Account.objects.create(
            user=self.user2, name='Запасной счет', account_type='cash', currency=self.currency, balance=Decimal(100)
        )

    def test_successful_transfer(self):
        data = {
            'sender_account': self.account1.id,
            'receiver_account': self.account2.id,
            'amount':'150.00',
            'description': 'Оплата услуг',
        }
        response = self.client.post('/api/transfer/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], '150.00')
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('350.00'))
        self.assertEqual(self.account2.balance, Decimal('250.00'))

    def test_transfer_same_account(self):
        data = {
            'sender_account': self.account1.id,
            'receiver_account': self.account1.id,
            'amount': '50.00',
            'description': 'Ошибка: перевод на тот же счет'
        }
        response = self.client.post('/api/transfer/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_transfer_insufficient_funds(self):
        data = {
            'sender_account': self.account1.id,
            'receiver_account': self.account2.id,
            'amount': '600.00',  # Больше, чем доступно на account1
            'description': 'Ошибка: недостаточно средств'
        }
        response = self.client.post('/api/transfer/', data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('Недостаточно средств на счете отправителя.', response.data['non_field_errors'])

    def test_invalid_data(self):
        data = {
            'from_account': self.account1.id,
            'to_account': self.account2.id,
        }
        response = self.client.post("/api/transfer/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(float(self.account1.balance), 500.00)
        self.assertEqual(float(self.account2.balance), 100.00)

    def test_transfer_negative_amount(self):
        data = {
            'sender_account': self.account1.id,
            'receiver_account': self.account2.id,
            'amount': '-50.00',
            'description': 'Ошибка: отрицательная сумма'
        }
        response = self.client.post('/api/transfer/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Сумма перевода должна быть больше нуля.', response.data['non_field_errors'])

    def test_transfer_unauthorized(self):
        self.client.logout()
        data = {
            'sender_account': self.account1.id,
            'receiver_account': self.account2.id,
            'amount': '50.00',
            'description': 'Перевод без авторизации'
        }
        response = self.client.post('/api/transfer/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
