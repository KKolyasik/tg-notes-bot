# TG Notes Bot

TG Notes Bot — телеграм-бот на базе **aiogram 3**, который помогает сохранять заметки и получать напоминания в нужное время. Проект включает полноценную инфраструктуру: PostgreSQL для хранения данных, Redis для очередей, Celery для фоновых задач и мини-приложение Telegram (TMA) для выбора времени напоминания.

## Возможности

- `/start` и главное меню с быстрыми кнопками.
- Пошаговое создание заметки с заголовком и необязательным текстом.
- Выбор времени напоминания через встроенное web-приложение.
- Планирование отправки напоминаний в Celery и доставка сообщений в Telegram точно по расписанию.
- Автоматическое создание карточки пользователя и хранение истории заметок в PostgreSQL.

## Архитектура

| Компонент | Описание |
|-----------|----------|
| `bot/` | Telegram-бот на aiogram: обработчики команд, FSM для создания заметок, работа с БД и Redis. |
| `bot/celery/` | Celery worker и beat: планирование (`check_reminders`) и отправка напоминаний (`send_reminder`). |
| `bot/models/` | SQLAlchemy-модели пользователей, заметок и напоминаний. |
| `web_picker/` | FastAPI-приложение для Telegram Mini App: выбор даты/времени и валидация `initData`. |
| `migrations/` | Alembic миграции для схемы БД. |
| `docker-compose.yml` | Оркестрация сервисов: Postgres, Redis, бот, Celery, web-picker. |

## Быстрый старт в Docker

1. Скопируйте `.env.example` (если отсутствует — создайте файл `.env` вручную) и заполните переменные окружения:
   ```dotenv
   BOT_TOKEN="123456789:your-bot-token"
   BASE_WEBAPP_URL="https://example.com"        # URL, который Telegram будет открывать для web-приложения
   REDIS_PASSWORD="strong_redis_password"
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_DB=0
   POSTGRES_DB=notes
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   ```
2. Запустите инфраструктуру:
   ```bash
   docker compose up --build
   ```
3. Убедитесь, что бот успешно авторизован и Celery worker/beat запущены. После этого откройте чат с ботом и введите `/start`.

> **Важно:** для web-приложения Telegram Mini App укажите публично доступный `BASE_WEBAPP_URL` (например, через прокси/туннель).

## Локальная разработка

1. Установите зависимости:
   ```bash
   poetry install
   ```
2. Поднимите PostgreSQL и Redis (можно через `docker compose up postgres redis`).
3. Примените миграции:
   ```bash
   alembic upgrade head
   ```
4. Запустите нужные процессы в отдельных терминалах:
   ```bash
   poetry run python -m bot.main              # Telegram-бот
   poetry run celery -A bot.celery.main.app beat -l INFO
   poetry run celery -A bot.celery.main.app worker -l INFO -P solo -Q reminders,maintenance --concurrency=4
   poetry run uvicorn web_picker.main:app --reload  # Web-приложение для выбора времени
   ```

## Взаимодействие с ботом

1. Выполните `/start` — бот отправит главное меню с кнопками «Создать новую заметку» и «Список заметок».
2. Нажмите «Создать новую заметку» или отправьте команду `/new`.
3. Следуйте подсказкам:
   - введите заголовок;
   - при необходимости — текст заметки или нажмите «Пропустить»;
   - выберите время через мини-приложение (отправляет ISO-дату в чат).
4. Получите подтверждение о создании заметки. В указанное время бот пришлёт напоминание.

## Полезные команды для разработки

- `alembic revision --autogenerate -m "message"` — создание новой миграции.
- `poetry run pytest` — запуск тестов (если появятся).
- `poetry run ruff check` / `poetry run black` — пример возможных линтеров и форматтера.

## Лицензия

Проект распространяется на условиях лицензии MIT (при необходимости замените на актуальную).
