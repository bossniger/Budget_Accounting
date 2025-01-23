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
        response = self.client.post('/api/v1/loans/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)