from datetime import date, timedelta
from decimal import Decimal
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from budget.models import Currency, Account, Counterparty, Loan


class LoanViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user3', password='password123')
        self.client.force_authenticate(user=self.user)
        self.currency = Currency.objects.create(code='EUR', name='ЕВРО', rate_to_base=Decimal('1.0'))
        self.account = Account.objects.create(
            user=self.user, name='Основной счет', account_type='cash', currency=self.currency, balance=Decimal('500.00')
        )
        self.counterparty = Counterparty.objects.create(name='ЗАО "Банк"', contact_info='8800555353', user=self.user)
        self.loan = Loan.objects.create(
            user=self.user,
            loan_type='received',
            principal_amount=Decimal('200.00'),
            interest_rate=Decimal('5.0'),
            currency=self.currency,
            account=self.account,
            date_issued=date.today(),
            due_date=date.today() + timedelta(days=30),
            description='Кредит на покупку',
            counterparty=self.counterparty,
        )

    def test_create_loan(self):
        data = {
            'loan_type': 'received',
            'principal_amount': '300.00',
            'interest_rate': '5.0',
            'currency': self.currency.id,
            'account': self.account.id,
            'date_issued': str(date.today()),
            'due_date': str(date.today() + timedelta(days=60)),
            'description': 'Новый кредит',
            'counterparty': self.counterparty.id,
        }
        response = self.client.post('/api/v1/loans/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_loans(self):
        response = self.client.get('/api/v1/loans/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_loan(self):
        response = self.client.get(f'/api/v1/loans/{self.loan.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.loan.id)
        self.assertEqual(response.data["principal_amount"], "200.00")
        self.assertEqual(response.data["remaining_amount"], "200.82")

    def test_update_loan(self):
        data = {
            "description": "Обновленное описание"
        }
        response = self.client.patch(f'/api/v1/loans/{self.loan.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.description, "Обновленное описание")

    def test_make_payment(self):
        data = {"amount": "50.00"}
        response = self.client.post(f'/api/v1/loans/{self.loan.id}/make_payment/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.loan.refresh_from_db()
        self.assertEqual(float(self.loan.remaining_amount), 150.82)

    def test_settle_loan(self):
        response = self.client.post(f'/api/v1/loans/{self.loan.id}/settle/', {'amount': '200.82'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.loan.refresh_from_db()
        self.assertTrue(self.loan.is_settled)
        self.assertEqual(float(self.loan.remaining_amount), 0.0)
