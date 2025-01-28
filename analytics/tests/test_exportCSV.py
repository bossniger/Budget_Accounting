import csv
import io
from datetime import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from budget.models import Category, Transaction


class ExportCSVViewTests(APITestCase):

    def setUp(self):
        # Создание пользователя и категории для теста
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name="Food")
        transaction_date_1 = timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0))
        transaction_date_2 = timezone.make_aware(datetime(2025, 1, 31, 0, 0, 0))
        self.transaction_1 = Transaction.objects.create(
            user=self.user,
            date=transaction_date_1,
            type='income',
            category=self.category,
            amount=100.00,
            description="Test transaction 1"
        )
        self.transaction_2 = Transaction.objects.create(
            user=self.user,
            date=transaction_date_2,
            type='expense',
            category=self.category,
            amount=50.00,
            description="Test transaction 2"
        )

        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

    def test_export_csv_success(self):
        # Проверка корректного экспорта транзакций в CSV
        url = '/api/analytics/export-csv/'
        params = {'start_date': '2025-01-01', 'end_date': '2025-01-31'}
        response = self.client.get(url, params)

        # Проверка статуса ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка, что это файл CSV
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename='))

        # Проверка содержимого CSV
        csv_file = io.StringIO(response.content.decode('utf-8'))
        reader = csv.reader(csv_file, delimiter=';')
        rows = list(reader)
        rows[0] = [cell.lstrip('\ufeff') for cell in rows[0]]
        # Проверка, что в CSV есть заголовки
        self.assertEqual(rows[0], ['Дата', 'Тип', 'Категория', 'Сумма', 'Описание'])

        # Проверка данных транзакций в CSV
        self.assertEqual(rows[1][0][:10], '2025-01-26')
        self.assertEqual(rows[2][0][:10], '2025-01-26')

    def test_export_csv_no_transactions(self):
        # Создание пустого фильтра (не существует транзакций в январе 2024)
        start_date = '2024-01-01'
        end_date = '2024-01-31'

        # Запрос на экспорт в CSV
        response = self.client.get(f'/api/analytics/export-csv/?start_date={start_date}&end_date={end_date}')

        # Проверка, что ответ успешен
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Чтение содержимого CSV
        content = response.content.decode('utf-8')
        rows = content.splitlines()

        # Проверка, что в CSV нет данных (только заголовки)
        self.assertEqual(len(rows), 1)  # Только заголовок
