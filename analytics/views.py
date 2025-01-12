import csv
from io import BytesIO

from django.db.models import Sum, Case, When, DecimalField
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from analytics.docs.analytics_docs import ANALYTICS_RESPONSE_EXAMPLE
from analytics.docs.top_expense_cat import TOP_EXPENSE_CATEGORIES_PARAMS, TOP_EXPENSE_CATEGORIES_RESPONSES
from budget.models import Transaction


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение аналитики по доходам и расходам за указанный период.",
        manual_parameters=[
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
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ с аналитическими данными",
                examples={"application/json": ANALYTICS_RESPONSE_EXAMPLE},
            ),
            400: "Неверный формат данных или отсутствуют обязательные параметры",
            401: "Пользователь не аутентифицирован",
        },
    )

    def get(self, request):
        if not request.user.is_authenticated:
            raise AuthenticationFailed(detail='Not authenticated')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {"error": "Пожалуйста, укажите start_date и end_date  формате YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response(
                {"error": "Неверный формат даты. Используйте YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Фильтрация транзакций по дате
        user = request.user
        transactions = Transaction.objects.filter(user=user,
                                                  date__date__gte=start_date,
                                                  date__date__lte=end_date
                                                  )

        # Агрегация данных
        analytics = transactions.values('category__name').annotate(
            total_income=Sum(
                Case(
                    When(type='income', then='amount'),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            total_expense=Sum(
                Case(
                    When(type='expense', then='amount'),
                    default=0,
                    output_field=DecimalField()
                )
            )
        )

        # Итоговые суммы
        total_income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
        print(f"Total income calculated: {total_income}")
        total_expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
        print(f"Total expense calculated: {total_expense}")

        return Response({
            "period": {"start_date": start_date, "end_date": end_date},
            "total_income": total_income,
            "total_expense": total_expense,
            "categories": list(analytics)  # данные по категориям
        })


class AnalyticsPageView(TemplateView):
    template_name = 'reports/user_manual_report.html'


class ExportCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        transactions = Transaction.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )
        # Генерация CVV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={start_date}-{end_date}.csv'
        response.write('\ufeff'.encode('utf8')) # поддержка utf-8 в экселе
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Дата', 'Тип', 'Категория', 'Сумма', 'Описание'])

        for transaction in transactions:
            writer.writerow([
                localtime(transaction.date).strftime('%Y-%m-%d %H:%M:%S'),
                transaction.type,
                transaction.category.name if transaction.category else "Без категории",
                transaction.amount,
                transaction.description or "_"
            ])
        return response


class ExportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        transactions = Transaction.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).select_related('category', 'account')

        # Настройка pdf
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Регистрация шрифта для кириллицы
        pdfmetrics.registerFont(TTFont("DejaVuSans", "static/fonts/DejaVuSans.ttf"))
        p.setFont("DejaVuSans", 12)

        # Заголовок
        p.drawString(100,750, f"Аналитика за период: {start_date} - {end_date}")

        # Отображение транзакций
        y = 720
        for transaction in transactions:
            line = (
                f"{transaction.date.strftime('%Y-%m-%d %H:%M:%S')} - "
                f"{transaction.type} - "
                f"{transaction.category.name if transaction.category else 'Без категории'} - "
                f"{transaction.description or '-'} - "
                f"{transaction.amount} - "
                f"{transaction.account.name if transaction.account else 'Не указан'}"
            )
            p.drawString(50, y, line)
            y -= 20
            if y < 50: # Создаем новую страницу, если заканчивается место
                p.showPage()
                p.setFont("DejaVuSans", 12)
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="analytics_{start_date}_to_{end_date}.pdf"'
        return response


class TopExpenseCategoriesView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение топ категорий расходов за указанный период",
        manual_parameters=[
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
        ],
        responses={
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
    )
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        # Кол-во категорий в топе. 5 по дефолту
        limit = int(request.query_params.get('limit', 5))
        if not start_date or not end_date:
            return Response(
                {'error': 'Пожалуйста, укажите start_date и end_date в формате YYYY-MM-DD'},
                status=400
            )
        try:
            transactions = Transaction.objects.filter(
                user=request.user,
                type='expense',
                date__date__gte=start_date,
                date__date__lte=end_date
            )
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD.'},
                status=400
            )

        top_categories = (
            transactions.values('category__name')
            .annotate(total_expense=Sum('amount'))
            .order_by('-total_expense')[:limit]
        )
        return Response({
            'period': {'start_date': start_date, 'end_date': end_date},
            'top_categories': list(top_categories)
        })