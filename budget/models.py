from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # Например USD, BYN...
    name = models.CharField(max_length=50)  # Полное название валюты
    rate_to_base = models.DecimalField(max_digits=10, decimal_places=4)  # Курс относительно базовой
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.code})'


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
        ('e_wallet', 'Электронный кошелек'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.user.username} - {self.balance} {self.currency.code}'

    def update_balance(self, amount: float):
        # Обновление остатка на счете
        self.balance += amount
        self.save()

    def get_transactions(self):
        # Получение транзакций, связанных с этим счетом
        return self.transactions.all()


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expence'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    account = models.ForeignKey(Account, related_name='transactions', on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, related_name='transactions', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        category_name = self.category.name if self.category else "Без категории"
        return f'{self.account.name} - {category_name} - {self.amount} {self.currency.code} - {self.date}'

    def save(self, *args, **kwargs):
        if not self.pk:  # Если транзакция новая
            if self.account:  # Обновляем баланс только если указан счет
                # Получаем конвертированную сумму, если валюты разные
                converted_amount = self.converted_amount

                # Обновляем баланс в зависимости от типа транзакции
                if self.type == 'expense':
                    self.account.update_balance(-converted_amount)  # Изменяем на сумму расхода
                elif self.type == 'income':
                    self.account.update_balance(converted_amount)  # Изменяем на сумму дохода

        super().save(*args, **kwargs)

    @property
    def converted_amount(self):
        """ Возвращает сумму, конвертированную в валюту счета. """
        if self.account.currency != self.currency:
            conversion_rate = self.currency.rate_to_base / self.account.currency.rate_to_base
            return self.amount * Decimal(conversion_rate)
        return self.amount  # Если валюта транзакции совпадает с валютой счета


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Transfer(models.Model):
    # Счет получателя
    sender_account = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='outgoing_transfers')
    # Счет отправителя
    receiver_account = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='incoming_transfers')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Transfer {self.amount} from {self.sender_account} to {self.receiver_account}'

    def save(self, *args, **kwargs):
        """
        При сохранении перевода обновляются балансы отправителя и получателя.
        """
        if self.sender_account == self.receiver_account:
            raise ValueError('Нельзя перевести средства между одинаковыми счетами.')
        if self.amount <=0:
            raise ValueError('Сумма перевода должна быть больше нуля.')
        if self.sender_account.balance < self.amount:
            raise ValueError('Недостаточно средств на счете отправителя.')

        self.sender_account.update_balance(-self.amount)
        self.receiver_account.update_balance(self.amount)
        super().save(*args, **kwargs)


     #  Бюджет на траты для определенной категории
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'{self.category.name} - {self.amount}'

    def get_total_expenses(self):
        # общая сумма расходов по данной категории
        return Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type='expense',
            date__range=(self.start_date, self.end_date)
        ).aggregate(total=Sum('amount'))['total'] or 0

    def is_exceeded(self):
        # Проверяем, не привышен ли бюджет.
        return self.get_total_expenses() > self.amount


class Counterparty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='counterparties')
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Loan(models.Model):
    LOAN_TYPES_CHOICES = [
        ('given', 'Выдано в долг'),
        ('received', 'Получено в кредит'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    counterparty = models.ForeignKey(Counterparty, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=8, choices=LOAN_TYPES_CHOICES)
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0) # Годовая ставка
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='loans')
    date_issued = models.DateField() # Дата создания кредита\долга
    due_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_settled = models.BooleanField(default=False)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def __str__(self):
        status= 'Погашен' if self.is_settled else 'Не погашен'
        return f'{self.get_loan_type_display()} - {self.principal_amount} {self.currency.code} ({status}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_amount = self.total_due
        super().save(*args, **kwargs)

    @property
    def total_due(self):
        # Преобразуем в Decimal для точных расчетов
        principal = Decimal(self.principal_amount)
        interest_rate = Decimal(self.interest_rate) / Decimal(100)

        # Рассчитываем количество лет между датами
        days_between = (self.due_date - self.date_issued).days
        years_between = Decimal(days_between) / Decimal(365)

        # Рассчитываем проценты
        interest = principal * interest_rate * years_between

        # Возвращаем сумму долга + проценты
        return principal + interest

    def make_payment(self, amount, payment_account=None):
        if self.is_settled:
            raise ValueError('Данный кредит уже погашен')
        if amount <= 0:
            raise ValueError('Сумма погашения должна быть больше 0')
        if amount > self.remaining_amount:
            raise ValueError('Сумма погашения превышает оставшуюся задолженность')
        # Уменьшаем остаток кредита
        self.remaining_amount -= amount
        # Обновляем баланс счета, если указан
        if payment_account:
            if self.loan_type == 'received':
                if payment_account.balance < amount:
                    raise ValueError('Недостаточно средств на счете для погашения кредита')
                payment_account.balance -= amount
            elif self.loan_type == 'given':
                payment_account.balance += amount
                payment_account.save()

        # Проверяем, полностью ли погашен кредит
        if self.remaining_amount == 0:
            self.is_settled = True

        self.save()

    def settle(self, payment_account=None):
        self.make_payment(self.remaining_amount, payment_account)
