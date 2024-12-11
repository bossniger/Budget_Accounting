from random import choice

import django_filters
from budget.models import Transaction


class TransactionFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='date')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte', label='Минимальная сумма')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte', label='Максимальная сумма')
    type = django_filters.ChoiceFilter(choices=Transaction.TRANSACTION_TYPE_CHOICES, label='Тип транзакции')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains', label='Категория')
    currency = django_filters.CharFilter(field_name="currency__code", lookup_expr="iexact")

    class Meta:
        model = Transaction
        fields = ['date','amount', 'type', 'category', 'currency']
