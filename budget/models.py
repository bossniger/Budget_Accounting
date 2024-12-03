from django.db import models
from django.contrib.auth.models import User
from sqlparse.sql import Values


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
        ('e_wallet', 'Электронный кошелек'),
    ]
    CURRENCY_CHOICES = [
        ('BYN', 'BYN'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.user.username}'

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

    def __str__(self):
        return f'{self.account.name} - {self.category.name} - {self.amount} - {self.date}'

    def save(self, *args, **kwargs):
        if not self.pk: # Если транзакция новая
            if self.account: # Обновляем баланс только если указан счет
                if self.type == 'expense':
                    self.account.update_balance(-self.amount)
                elif self.type == 'income':
                    self.account.update_balance(self.amount)
        super().save(*args, **kwargs)



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