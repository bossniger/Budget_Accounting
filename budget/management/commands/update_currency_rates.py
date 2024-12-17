import requests
from django.core.management.base import BaseCommand
from budget.models import Currency

# API НБРБ для получения курсов валют
NBRB_API_URL = "https://www.nbrb.by/api/exrates/rates?periodicity=0"

class Command(BaseCommand):
    help = "Обновление курсов валют из API НБРБ"

    def handle(self, *args, **kwargs):
        supported_currencies = ['EUR', 'USD']  # Поддерживаемые валюты
        self.stdout.write("Запрос курсов валют из API НБРБ...")

        # Отправляем запрос к API
        try:
            response = requests.get(NBRB_API_URL)
            response.raise_for_status()
            rates_data = response.json()
        except requests.RequestException as e:
            self.stderr.write(f"Ошибка запроса к API НБРБ: {e}")
            return

        # Обрабатываем данные и обновляем курсы
        for rate_info in rates_data:
            currency_code = rate_info["Cur_Abbreviation"]

            # Проверяем, входит ли валюта в список поддерживаемых
            if currency_code in supported_currencies:
                official_rate = rate_info["Cur_OfficialRate"]
                scale = rate_info["Cur_Scale"]

                try:
                    # Проверяем scale на корректность
                    if scale == 0:
                        self.stderr.write(f"Ошибка данных для {currency_code}: scale = 0")
                        continue

                    # Переводим курс к одной единице валюты
                    normalized_rate = official_rate / scale

                    # Обновляем курс в базе данных
                    currency = Currency.objects.get(code=currency_code)
                    currency.rate_to_base = normalized_rate  # Обновляем курс относительно BYN
                    currency.save()

                    self.stdout.write(
                        f"Обновлено: {currency_code} = {normalized_rate:.4f} BYN (за {scale} ед.)"
                    )
                except Currency.DoesNotExist:
                    self.stderr.write(f"Валюта {currency_code} не найдена в базе.")
                except Exception as e:
                    self.stderr.write(f"Ошибка обработки валюты {currency_code}: {e}")

        self.stdout.write("Обновление курсов завершено.")
