from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from budget.models import Budget
from datetime import date


@shared_task
def check_budgets():
    """
    Проверяет все бюджеты на превышение и отправляет уведомления пользователям.
    """
    today = date.today()
    budgets = Budget.objects.filter(start_date__lte=today, end_date__gte=today)

    for budget in budgets:
        total_expenses = budget.get_total_expenses()
        if total_expenses > budget.amount:
            # Отправляем уведомление
            subject = "Превышение бюджета!"
            message = (
                f"Ваш бюджет по категории {budget.category.name} "
                f"превышен! Общие расходы: {total_expenses}, "
                f"запланированный бюджет: {budget.amount}."
            )
            recipient = budget.user.email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
