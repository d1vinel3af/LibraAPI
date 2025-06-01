# Этап сборки
FROM python:3.13-alpine as builder

# Устанавливаем зависимости, необходимые для сборки
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev postgresql-dev

# Устанавливаем Poetry
RUN pip install --upgrade pip && \
    pip install poetry==2.1.2

# Настраиваем рабочую директорию
WORKDIR /app

# Копируем только файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости без dev-зависимостей и без установки текущего проекта
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

# Копируем остальные файлы приложения
COPY . .

# Этап выполнения
FROM python:3.13-alpine

# Устанавливаем runtime зависимости
RUN apk add --no-cache libffi openssl

# Копируем установленные зависимости из builder-этапа
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /app /app

# Настраиваем рабочую директорию
WORKDIR /app/libraapi

# Запускаем FastAPI с uvicorn (пример)
CMD ["python", "main.py"]