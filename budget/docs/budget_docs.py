from drf_yasg import openapi

# Пример ответа для списка бюджетов
BUDGET_LIST_RESPONSE = openapi.Response(
    description="Список бюджетов текущего пользователя",
    examples={
        "application/json": [
            {
                "id": 1,
                "category": "Food",
                "amount": "1000.00",
                "start_date": "2024-12-01",
                "end_date": "2024-12-31"
            },
            {
                "id": 2,
                "category": "Transport",
                "amount": "500.00",
                "start_date": "2024-12-01",
                "end_date": "2024-12-31"
            }
        ]
    },
)

# Пример запроса для создания бюджета
BUDGET_CREATE_EXAMPLE = {
    "category": 1,  # ID категории
    "amount": "1500.00",
    "start_date": "2024-12-01",
    "end_date": "2024-12-31",
}

# Пример ответа для создания бюджета
BUDGET_CREATE_RESPONSE = openapi.Response(
    description="Бюджет успешно создан",
    examples={
        "application/json": {
            "id": 3,
            "category": "Health",
            "amount": "1500.00",
            "start_date": "2024-12-01",
            "end_date": "2024-12-31",
        }
    },
)
