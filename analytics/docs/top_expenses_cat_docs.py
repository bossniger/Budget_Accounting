from drf_yasg import openapi

TOP_EXPENSE_CATEGORIES_DOCS = {
    "operation_description": "Получение аналитики по топ категориям расходов.",
    "manual_parameters": [
        openapi.Parameter(
            "start_date",
            openapi.IN_QUERY,
            description="Дата начала периода (формат YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "end_date",
            openapi.IN_QUERY,
            description="Дата окончания периода (формат YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "limit",
            openapi.IN_QUERY,
            description="Количество категорий в отчете (по умолчанию 5).",
            type=openapi.TYPE_INTEGER,
            required=False,
        ),
    ],
    "responses": {
        200: openapi.Response(
            description="Успешный ответ с данными по категориям расходов",
            examples={
                "application/json": {
                    "period": {
                        "start_date": "2024-12-01",
                        "end_date": "2024-12-31",
                    },
                    "categories": [
                        {"category_name": "Еда", "total_expense": 150.0},
                        {"category_name": "Развлечения", "total_expense": 120.0},
                    ],
                }
            },
        ),
        400: "Неверный формат данных или отсутствуют обязательные параметры",
        401: "Пользователь не аутентифицирован",
    },
}