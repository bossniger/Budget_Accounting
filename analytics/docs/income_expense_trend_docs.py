from drf_yasg import openapi

INCOME_EXPENSE_TREND_DOCS = {
    'operation_description': "Получение динамики доходов и расходов за определенный период",
    'manual_parameters': [
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
            "group_by",
            openapi.IN_QUERY,
            description="Группировка по дням ('day'), неделям ('week') или месяцам ('month')",
            type=openapi.TYPE_STRING,
            enum=["day", "week", "month"],
            required=True,
        ),
    ],
    'responses': {
    200: openapi.Response(
        description="Успешный ответ с данными динамики расходов и доходов",
        examples={
            "application/json": {
                "period": {
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-31",
                },
                "trend": [
                    {
                        "date": "2024-12-01",
                        "total_income": 200.0,
                        "total_expense": 100.0,
                    },
                    {
                        "date": "2024-12-02",
                        "total_income": 150.0,
                        "total_expense": 50.0,
                    },
                ],
            }
        },
    ),
    400: "Неверный формат данных или отсутствуют обязательные параметры",
    401: "Пользователь не аутентифицирован",
    },
}
