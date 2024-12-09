import csv
from io import BytesIO

from django.db.models import Sum, Case, When, DecimalField
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.views.generic import TemplateView
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

from budget.models import Transaction


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

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
        total_expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0

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
