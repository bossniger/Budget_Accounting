from drf_yasg import openapi

# Пример ответа для списка категорий
CATEGORY_LIST_RESPONSE = openapi.Response(
    description="Список категорий",
    examples={
        "application/json": [
            {"id": 1, "name": "Food", "description": "Expenses for food"},
            {"id": 2, "name": "Transport", "description": "Expenses for transport"},
        ]
    },
)

# Пример ответа для создания категории
CATEGORY_CREATE_RESPONSE = openapi.Response(
    description="Категория успешно создана",
    examples={
        "application/json": {
            "id": 3,
            "name": "Health",
            "description": "Medical expenses",
        }
    },
)

# Параметры фильтрации (если нужны)
CATEGORY_FILTER_PARAMS = [
    openapi.Parameter(
        'name', openapi.IN_QUERY,
        description="Фильтр по названию категории (частичное совпадение)",
        type=openapi.TYPE_STRING,
    )
]
