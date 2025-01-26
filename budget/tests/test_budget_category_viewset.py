from datetime import date, timedelta

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from budget.models import Category, Budget


class BudgetViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user3', password='password123')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Еда')
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=300.00,
            start_date=date.today() - timedelta(days=15),
            end_date=date.today() + timedelta(days=15)
        )

    def test_list_budgets(self):
        response = self.client.get('/api/v1/budgets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_budget(self):
        response = self.client.get(f'/api/v1/budgets/{self.budget.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.budget.id)

    def test_create_budget(self):
        data = {
            'category': self.category.id,
            'amount': '400.00',
            'start_date': (date.today() + timedelta(days=31)).isoformat(),
            'end_date': (date.today() + timedelta(days=90)).isoformat()
        }
        response = self.client.post('/api/v1/budgets/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], '400.00')

    def test_update_budget(self):
        data = {
            'category': self.category.id,
            'amount': '600.00',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=90)).isoformat()
        }
        response = self.client.put(f'/api/v1/budgets/{self.budget.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '600.00')

    def test_check_budget_status(self):
        response = self.client.get(f'/api/v1/budgets/{self.budget.id}/check_budget_status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_expenses', response.data)
        self.assertIn('is_exceeded', response.data)

    def test_summary(self):
        response = self.client.get('/api/v1/budgets/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('total_expenses', response.data[0])
        self.assertIn('is_exceeded', response.data[0])
