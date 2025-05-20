FROM python:3.11-slim

WORKDIR /app

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Встановлення wkhtmltopdf (потрібно для генерації PDF)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копіювання файлів залежностей
COPY requirements.txt .

# Встановлення Python залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання проекту
COPY . .

# Створення необхідних директорій
RUN mkdir -p media static logs results

# Налаштування прав доступу
RUN chmod +x /app/manage.py

# Відкриття порту
EXPOSE 8000

# Запуск команди для старту сервера
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
