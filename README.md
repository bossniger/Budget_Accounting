# Budget Accounting API

## Описание
Проект "Budget Accounting" — это API для учета доходов, расходов, кредитов, долгов и других финансовых операций. Включает функционал работы с бюджетами, аналитикой и экспортом данных.

---

## Требования
- Docker версии 20.10.0 или выше
- Docker Compose версии 1.27.0 или выше

## Установка и запуск

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/bossniger/Budget_Accounting.git
   cd Budget_Accounting
   ```

2. **Создать `.env` файл:**

   Создайте файл `.env` в корне проекта и укажите в нем переменные окружения:

   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=budget_accounting
   SECRET_KEY=django-insecure-1afr5)2%&tum+6u=q1v=ym0yr73&nlmy6l9lb4td3x-ku%!7kv
   DJANGO_ALLOWED_HOSTS=*
   DEBUG=False
   ```

3. **Собрать и запустить контейнеры:**

   ```bash
   docker-compose up --build -d
   ```
   - `--build`: пересобирает образы Docker.
   - `-d`: запускает контейнеры в фоновом режиме.
   - 
4. **Применить миграции базы данных:**

   Выполните миграции для инициализации базы данных:

   ```bash
   docker-compose exec app python manage.py migrate
   ```

5. **Собрать статические файлы:**

   Для корректного отображения админки и Swagger интерфейса выполните команду:

   ```bash
   docker-compose exec app python manage.py collectstatic --noinput
   ```

6. **Создать суперпользователя:**

   Для доступа к Django Admin создайте суперпользователя:

   ```bash
   docker-compose exec app python manage.py createsuperuser
   ```

7. **Доступ к приложению:**

   После успешного деплоя приложение будет доступно по адресу:

   ```
   http://localhost:8000
   ```

   Админка: `http://localhost:8000/admin`
   Swagger: 'http://localhost:8000/swagger'

8. **Логи приложения:**

   Для просмотра логов используйте команду:

   ```bash
   docker-compose logs -f app
   ```

9. **Остановка приложения:**

   Чтобы остановить контейнеры, выполните:

   ```bash
   docker-compose down
   ```
   ### Дополнительно

- **Проверка состояния контейнеров:**

   ```bash
   docker-compose ps
   ```

- **Перезапуск приложения:**

   ```bash
   docker-compose restart app
   ```

- **Удаление томов базы данных:**

   Чтобы полностью удалить данные и контейнеры:

   ```bash
   docker-compose down -v
   ```

---

Теперь приложение готово к использованию!