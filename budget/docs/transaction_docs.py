from drf_yasg import openapi

# Параметры фильтрации
TRANSACTION_FILTER_PARAMS = [
    openapi.Parameter(
        'date_from', openapi.IN_QUERY,
        description="Фильтр по начальной дате (YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
        format='date',
    ),
    openapi.Parameter(
        'date_to', openapi.IN_QUERY,
        description="Фильтр по конечной дате (YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
        format='date',
    ),
    openapi.Parameter(
        'type', openapi.IN_QUERY,
        description="Фильтр по типу транзакции (например, 'expense', 'income')",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        'category', openapi.IN_QUERY,
        description="Фильтр по категории транзакции (например, 'Food', 'Transport')",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        'ordering', openapi.IN_QUERY,
        description="Сортировка по полям (например, 'date' или '-amount')",
        type=openapi.TYPE_STRING,
    ),
]

# Пример ответа
TRANSACTION_LIST_RESPONSE = openapi.Response(
    description="Список транзакций",
    examples={
        "application/json": [
            {"id": 1, "category": "Food", "type": "expense", "amount": 50.0, "date": "2024-12-10"},
            {"id": 2, "category": "Transport", "type": "expense", "amount": 20.0, "date": "2024-12-11"},
        ]
    },
)