# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    cmake

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

RUN /bin/bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"


# Применяем миграции
RUN python manage.py makemigrations clinicApp
RUN python manage.py migrate

# Создаем суперпользователя (если необходимо, можно автоматизировать создание суперпользователя)
# ENV DJANGO_SUPERUSER_USERNAME=admin
# ENV DJANGO_SUPERUSER_PASSWORD=admin
# ENV DJANGO_SUPERUSER_EMAIL=admin@example.com
# RUN python manage.py createsuperuser --noinput

# Команда для запуска сервера Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
