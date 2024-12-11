from drf_yasg import openapi

# Пример запроса
ANALYTICS_REQUEST_EXAMPLE = {
    "start_date": "2024-12-01",
    "end_date": "2024-12-31"
}

# Пример ответа
ANALYTICS_RESPONSE_EXAMPLE = {
    "period": {
        "start_date": "2024-12-01",
        "end_date": "2024-12-31"
    },
    "total_income": "5000.00",
    "total_expense": "3000.00",
    "categories": [
        {
            "category__name": "Food",
            "total_income": "0.00",
            "total_expense": "1200.00"
        },
        {
            "category__name": "Salary",
            "total_income": "5000.00",
            "total_expense": "0.00"
        }
    ]
}
