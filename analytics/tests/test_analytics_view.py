from django.utils.timezone import make_aware
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from budget.models import Transaction, Category, Account, Currency
from datetime import datetime

class AnalyticsViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.account = Account.objects.create(
            user=self.user,
            name="Основной счет",
            account_type="cash",
            currency=Currency.objects.create(code="BYN", name="Белорусский рубль", rate_to_base=1),
            balance=1000
        )
        self.category_income = Category.objects.create(name="Зарплата")
        self.category_expense1 = Category.objects.create(name="Автомобиль")
        self.category_expense2 = Category.objects.create(name="Девочки")

        Transaction.objects.create(
            user=self.user,
            account=self.account,
            type="income",
            amount=235.48,
            category=self.category_income,
            currency=self.account.currency,
            date=make_aware(datetime(2024, 12, 5))
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            type="expense",
            amount=2.0,
            category=self.category_expense1,
            currency=self.account.currency,
            date=make_aware(datetime(2024, 12, 15))
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            type="expense",
            amount=101.0,
            category=self.category_expense2,
            currency=self.account.currency,
            date=make_aware(datetime(2024, 12, 20))
        )
        self.client.login(username="testuser", password="testpassword")
        self.url = "/api/analytics/analytics/"

        # Проверяем созданные транзакции
        print("Created transactions:", list(Transaction.objects.all()))

    def test_successful_analytics(self):
        response = self.client.get(self.url, {"start_date": "2024-12-01", "end_date": "2025-01-31"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем общие доходы и расходы
        print(response.data)
        self.assertEqual(round(float(response.data["total_income"]), 2), 235.48)
        self.assertEqual(response.data["total_expense"], 103.0)

        # Проверяем данные по категориям
        categories = response.data["categories"]
        self.assertEqual(len(categories), 3)
        self.assertEqual(categories[0]["category__name"], "Автомобиль")
        self.assertEqual(categories[0]["total_income"], 0.0)
        self.assertEqual(categories[0]["total_expense"], 2.0)

        self.assertEqual(categories[1]["category__name"], "Девочки")
        self.assertEqual(categories[1]["total_income"], 0.0)
        self.assertEqual(categories[1]["total_expense"], 101.0)

        self.assertEqual(categories[2]["category__name"], "Зарплата")
        self.assertEqual(float(categories[2]["total_income"]), 235.48)
        self.assertEqual(categories[2]["total_expense"], 0.0)

    def test_missing_parameters(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Пожалуйста, укажите start_date и end_date", response.data["error"])

    def test_invalid_date_format(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.url, {"start_date": "2024-12-01", "end_date": "12/2024"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Неверный формат даты", response.data["error"])

    def test_unauthenticated_user(self):
        self.client.force_authenticate(user=None)  # Убедиться, что пользователь не аутентифицирован
        response = self.client.get(self.url, {"start_date": "2024-12-01", "end_date": "2024-12-31"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)