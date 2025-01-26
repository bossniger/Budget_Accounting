from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from budget.models import Account, Currency


class AccountViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.currency = Currency.objects.create(code='BYN', name='Белорусский рубль', rate_to_base=Decimal(1))
        self.account1 = Account.objects.create(
            user=self.user, name='Основной счет', account_type='cash', currency=self.currency, balance=Decimal(500.00)
        )
        self.account2 = Account.objects.create(
            user=self.user, name='Дополнительный счет', account_type='card', currency=self.currency,
            balance=Decimal(100.00)
        )
        self.new_account_data = {
            'name': 'Новый счет',
            'account_type': 'e_wallet',
            'currency': self.currency.id
        }

    def test_list_accounts(self):
        response = self.client.get('/api/v1/accounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_account(self):
        response = self.client.get(f'/api/v1/accounts/{self.account1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Основной счет')
        self.assertEqual(float(response.data['balance']), 500.00)

    def test_create_account(self):
        response = self.client.post('/api/v1/accounts/', self.new_account_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Новый счет')

    def test_update_account(self):
        update_data = {'name': 'Обновленный счет'}
        response = self.client.patch(f'/api/v1/accounts/{self.account1.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.name, 'Обновленный счет')

    def test_delete_account(self):
        response = self.client.delete(f'/api/v1/accounts/{self.account1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Account.objects.filter(id=self.account1.id).exists())

    def test_deposit_positive_amount(self):
        data = {'amount': 200.00}
        response = self.client.post(f'/api/v1/accounts/{self.account1.id}/deposit/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account1.refresh_from_db()
        self.assertEqual(float(self.account1.balance), 700.00)

    def test_deposit_negative_amount(self):
        data = {'amount': -50.00}
        response = self.client.post(f'/api/v1/accounts/{self.account1.id}/deposit/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Сумма должна быть положительным числом')

    def test_deposit_invalid_amount(self):
        data = {'amount': 'invalid'}
        response = self.client.post(f'/api/v1/accounts/{self.account1.id}/deposit/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Укажите корректную сумму.')

    def test_access_denied_for_other_users(self):
        user2 = User.objects.create_user(username='otheruser', password='password123')
        self.client.force_authenticate(user=user2)
        response = self.client.get(f'/api/v1/accounts/{self.account1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Другой пользователь не должен иметь доступ
