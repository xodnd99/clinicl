# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    cmake \
    postgresql-client

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Активируем виртуальное окружение и устанавливаем зависимости
RUN /bin/bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Устанавливаем дополнительный пакет для пагинации
RUN /bin/bash -c "source venv/bin/activate && pip install django-paginate"

# Применяем миграции
RUN /bin/bash -c "source venv/bin/activate && python manage.py makemigrations clinicApp"
RUN /bin/bash -c "source venv/bin/activate && python manage.py migrate"

# Команда для запуска сервера Django
CMD ["/bin/bash", "-c", "source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"]

