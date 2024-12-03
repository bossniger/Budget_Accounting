from rest_framework import serializers
from .models import Transaction, Category, Tag, Account, Transfer
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'type', 'amount', 'date', 'description', 'category', 'tags']


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
        - Проверка, что счет отправителя принадлежит текущему пользователю.
        """
        user = self.context['request'].user

        if data['sender_account'] == data['receiver_account']:
            raise serializers.ValidationError("Нельзя перевести средства между одинаковыми счетами.")
        if data['amount'] <= 0:
            raise serializers.ValidationError("Сумма перевода должна быть больше нуля.")
        if data['sender_account'].balance < data['amount']:
            raise serializers.ValidationError("Недостаточно средств на счете отправителя.")
        if data['sender_account'].user!=user:
            raise serializers.ValidationError("Вы можете переводить средства только со своего счета")
        return data