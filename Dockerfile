# Используем базовый образ Python
FROM python:3.12

# Устанавливаем зависимости для CMake
RUN apt-get update && apt-get install -y cmake

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Активируем виртуальное окружение и устанавливаем зависимости
RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Применяем миграции
RUN . venv/bin/activate && python manage.py makemigrations clinicApp && python manage.py migrate

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска сервера
CMD ["sh", "-c", ". venv/bin/activate && python manage.py runserver 0.0.0.0:8000"]



