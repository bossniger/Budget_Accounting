from drf_yasg import openapi

TRANSACTION_LIST_PARAMETERS = [
    openapi.Parameter(
        "start_date",
        openapi.IN_QUERY,
        description="Дата начала периода фильтрации (формат YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "end_date",
        openapi.IN_QUERY,
        description="Дата окончания периода фильтрации (формат YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "min_amount",
        openapi.IN_QUERY,
        description="Минимальная сумма транзакции",
        type=openapi.TYPE_NUMBER,
    ),
    openapi.Parameter(
        "max_amount",
        openapi.IN_QUERY,
        description="Максимальная сумма транзакции",
        type=openapi.TYPE_NUMBER,
    ),
    openapi.Parameter(
        "category",
        openapi.IN_QUERY,
        description="Название категории транзакции (например, 'Еда', 'Развлечения')",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "description",
        openapi.IN_QUERY,
        description="Ключевое слово для поиска в описании транзакций",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "tags",
        openapi.IN_QUERY,
        description="Теги, связанные с транзакцией",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "ordering",
        openapi.IN_QUERY,
        description="Поле для сортировки. Например: 'amount', '-amount', 'date', '-date'",
        type=openapi.TYPE_STRING,
    ),
]

TRANSACTION_LIST_RESPONSES = {
    200: openapi.Response(
        description="Успешный ответ с данными о транзакциях",
        examples={
            "application/json": {
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": 1,
                        "user": 1,
                        "amount": "100.00",
                        "currency": {"code": "USD", "name": "Доллар США"},
                        "category": {"id": 1, "name": "Еда"},
                        "type": "expense",
                        "description": "Обед в кафе",
                        "date": "2024-12-01T12:00:00Z",
                        "account": {"id": 1, "name": "Основной счет"},
                    },
                    {
                        "id": 2,
                        "user": 1,
                        "amount": "500.00",
                        "currency": {"code": "BYN", "name": "Белорусский рубль"},
                        "category": {"id": 2, "name": "Зарплата"},
                        "type": "income",
                        "description": "Зарплата за декабрь",
                        "date": "2024-12-31T18:00:00Z",
                        "account": {"id": 1, "name": "Основной счет"},
                    },
                ],
            }
        },
    ),
    400: "Ошибка запроса (например, неверный формат даты)",
    401: "Пользователь не аутентифицирован",
}
