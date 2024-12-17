from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Указываем Django настройки для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Budget_Accounting.settings')

app = Celery('Budget_Accounting')

# Загружаем конфигурацию из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи в приложениях
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
