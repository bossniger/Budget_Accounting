from django.core.management.base import BaseCommand
import requests
from budget.models import Currency  # Убедитесь, что импортируете модель Currency

class Command(BaseCommand):
    help = "Обновляет курсы валют"

    def handle(self, *args, **kwargs):
        BASE_CURRENCY = 'USD'  # Базовая валюта
        API_URL = f"https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}"

        response = requests.get(API_URL)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Ошибка получения данных от API"))
            return

        data = response.json()
        rates = data['rates']  # Извлекаем курсы для всех валют

        for code, rate in rates.items():
            currency, created = Currency.objects.update_or_create(
                code=code,
                defaults={'rate_to_base': rate, 'name': code}  # Можно загрузить полное название из другого источника
            )
            action = "Создана" if created else "Обновлена"
            self.stdout.write(f"{action} валюта {currency.code}: {currency.rate_to_base}")

        self.stdout.write(self.style.SUCCESS("Курсы валют обновлены"))