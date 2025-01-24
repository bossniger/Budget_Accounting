from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from budget.models import Category


class BudgetViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user3', password='password123')
        self.client = APIClient()
        self.client.login(username='user3', password='password123')
        self.category = Category.objects.create(name='Еда')

    def test_create_budget(self):
        data = {
            'category': self.category.id,
            'amount': '500.00',
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'user': self.user.id,
        }
        response = self.client.post('/api/v1/budgets/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['category'], self.category.id)
        self.assertEqual(float(response.data['amount']),500.00)
        self.assertEqual(response.data['total_expenses'], '0')
        self.assertFalse(response.data['is_exceeded'])