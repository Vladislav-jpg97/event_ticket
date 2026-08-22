FROM python:3.13-slim

WORKDIR /app

# Установка системных зависимостей для сборки asyncpg и работы с PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Конфигурация Poetry: отключаем создание виртуального окружения внутри контейнера
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копируем весь исходный код и конфигурации миграций
COPY . .

EXPOSE 8000

# Команда для запуска приложения с учетом вашей структуры папок (src.backend.main:app)
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]