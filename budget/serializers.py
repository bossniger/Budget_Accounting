from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Transaction, Category, Tag, Account, Transfer, Budget, Currency, Counterparty, Loan
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['code', 'name', 'rate_to_base']
        read_only_fields = ['updated_at']

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    if from_currency.rate_to_base == 0:
        raise ValueError(f'Курс для {from_currency.code} не установлен')
    # конвертируем в базовую, а затем в целевую валюту
    base_amount = amount / from_currency.rate_to_base
    return base_amount * to_currency.rate_to_base


class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id','user', 'amount', 'currency', 'category', 'type', 'description', 'date', 'account', 'tags']

        def create(self, validated_data):
            account = validated_data['account']
            transaction_currency = validated_data.get('currency', account.currency)
            # Конвертируем если валюта не совпадает
            if transaction_currency != account.currency:
                validated_data['amount'] = convert_currency(
                    amount=validated_data['amount'],
                    from_currency=transaction_currency,
                    to_currency=account.currency
                )
            # обновляем баланс счета
            if validated_data['type'] == 'income':
                account.balance += validated_data['amount']
            elif validated_data['type'] == 'expense':
                account.balance -= validated_data['amount']
            account.save()
            return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'user', 'name', 'account_type', 'currency', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'balance', 'created_at', 'updated_at']

    # Создание нового счета. Пользователь автоматически связывается с учеткой
    def create(self, validated_data):
        user = self.context['request'].user # Получаем пользователя из контекста
        validated_data['user'] = user # Связываем счет с текущим пользователем
        return super().create(validated_data)


    def update(self, instance, validated_data):
        """
        Обновление счета. Разрешено изменение имени, типа и валюты.
        Баланс обновляется через другие методы (например, транзакции).
        """
        instance.name = validated_data.get('name', instance.name)
        instance.account_type = validated_data.get('account_type', instance.account_type)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.save()
        return instance


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['id', 'sender_account', 'receiver_account', 'amount', 'date', 'description']
        read_only_fields = ['id', 'date']

    def validate(self, data):
        """
        Дополнительные проверки:
        - Нельзя переводить на тот же счет.
        - Сумма перевода должна быть больше нуля.
        """

        if data['sender_account'] == data['receiver_account']:
            raise serializers.ValidationError("Нельзя перевести средства между одинаковыми счетами.")
        if data['amount'] <= 0:
            raise serializers.ValidationError("Сумма перевода должна быть больше нуля.")
        if data['sender_account'].balance < data['amount']:
            raise serializers.ValidationError("Недостаточно средств на счете отправителя.")
        return data


class BudgetSerializer(serializers.ModelSerializer):
    total_expenses = serializers.SerializerMethodField()
    is_exceeded = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['user', 'total_expenses', 'is_exceeded']

    def get_is_exceeded(self, obj):
        # Проверяем, превышен ли бюджет
        return obj.is_exceeded()

    def get_total_expenses(self, obj):
        return str(obj.get_total_expenses())

    def validate(self, data):
        user = self.context['request'].user
        overlapping_budgets = Budget.objects.filter(
            user=user,
            category=data['category'],
            start_date__lte=data['end_date'],
            end_date__gte=data['start_date']
        ).exclude(pk=self.instance.pk if self.instance else None)

        if overlapping_budgets.exists():
            raise ValidationError("Бюджет на этот период для данной категории уже существует.")
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class CounterpartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    counterparty = serializers.PrimaryKeyRelatedField(queryset=Counterparty.objects.all())
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    class Meta:
        model = Loan
        fields = [
            'id', 'loan_type', 'principal_amount', 'interest_rate',
            'currency', 'account', 'date_issued', 'due_date',
            'description', 'is_settled', 'remaining_amount', 'counterparty',
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        if data.get('due_date') and data['due_date'] < data['date_issued']:
            raise serializers.ValidationError("Дата погашения не может быть раньше даты выдачи.")
        return data
