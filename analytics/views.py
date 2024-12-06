from django.db.models import Sum, Case, When, DecimalField
from django.views.generic import TemplateView
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
            "categories": list(analytics) # данные по категориям
        })


class AnalyticsPageView(TemplateView):
    template_name = 'reports/user_manual_report.html'
