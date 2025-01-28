from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

TOP_EXPENSE_CATEGORIES_PARAMS = [
    openapi.Parameter(
        "start_date",
        openapi.IN_QUERY,
        description="Дата начала периода (формат YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
        required=True
    ),
    openapi.Parameter(
        "end_date",
        openapi.IN_QUERY,
        description="Дата окончания периода (формат YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
        required=True
    ),
    openapi.Parameter(
        "limit",
        openapi.IN_QUERY,
        description="Количество категорий в топе (по умолчанию 5)",
        type=openapi.TYPE_INTEGER,
        required=False
    ),
]

# Примеры ответов
TOP_EXPENSE_CATEGORIES_RESPONSES = {
    200: openapi.Response(
        description="Успешный ответ с топ категориями расходов",
        examples={
            "application/json": {
                "period": {
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-31"
                },
                "top_categories": [
                    {"category__name": "Развлечения", "total_expense": 500.00},
                    {"category__name": "Транспорт", "total_expense": 300.00},
                    {"category__name": "Продукты", "total_expense": 200.00}
                ]
            }
        }
    ),
    400: "Неверный формат даты или отсутствуют обязательные параметры",
    401: "Пользователь не аутентифицирован",
}