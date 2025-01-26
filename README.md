# Budget Accounting API

## Описание
Проект "Budget Accounting" — это API для учета доходов, расходов, кредитов, долгов и других финансовых операций. Включает функционал работы с бюджетами, аналитикой и экспортом данных.

---

## Требования
- Python 3.10+
- Django 4.x
- PostgreSQL (или SQLite для локального тестирования)
- Docker (для деплоя)
- Node.js (если требуется сборка фронтенда)

---

## Установка и запуск (локально)

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/bossniger/Budget_Accounting.git
   cd budget-accounting

2. **Создайте виртуальное окружение и активируйте его**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # (Linux/Mac)
    venv\Scripts\activate     # (Windows)

3. **Установите зависимости**:
    ```bash
    pip install -r requirements.txt
   
4. **Примените миграции**:
    ```bash
    python manage.py migrate

5. **Создайте суперпользователя**:
   ```bash
    python manage.py createsuperuser

6. **Запустите сервер**:
   ```bash
    python manage.py runserver
   
7. **Откройте приложение в браузере**:
- Админ-панель: http://127.0.0.1:8000/admin/ 
- Swagger-документация: http://127.0.0.1:8000/swagger/