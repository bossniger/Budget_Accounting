from drf_yasg import openapi

make_payment_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "amount": openapi.Schema(
            type=openapi.TYPE_NUMBER,
            description="Сумма платежа для погашения займа или кредита",
        )
    },
    required=["amount"],
    example={"amount": 500.0}
)

make_payment_response = openapi.Response(
    description="Успешный ответ после внесения платежа",
    examples={
        "application/json": {
            "id": 1,
            "type": "loan",
            "amount": 1000.0,
            "interest_rate": 5.0,
            "duration": 12,
            "borrower": {"id": 2, "name": "John Doe"},
            "creditor": {"id": 3, "name": "Jane Smith"},
            "total_due": 550.0,
            "status": "active",
            "created_at": "2025-01-01",
            "updated_at": "2025-01-15"
        }
    }
)

settle_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "amount": openapi.Schema(
            type=openapi.TYPE_NUMBER,
            description="Полная сумма для закрытия кредита или займа",
        )
    },
    required=["amount"],
    example={"amount": 1000.0}
)

settle_response = openapi.Response(
    description="Успешный ответ после полного погашения кредита или займа",
    examples={
        "application/json": {
            "id": 1,
            "type": "loan",
            "amount": 1000.0,
            "interest_rate": 5.0,
            "duration": 12,
            "borrower": {"id": 2, "name": "John Doe"},
            "creditor": {"id": 3, "name": "Jane Smith"},
            "total_due": 0.0,
            "status": "closed",
            "created_at": "2025-01-01",
            "updated_at": "2025-01-15"
        }
    }
)
