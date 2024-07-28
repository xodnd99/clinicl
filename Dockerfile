FROM python:3.12

RUN apt-get update && apt-get install -y cmake
RUN pip install --upgrade pip

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt



EXPOSE 8000

CMD ["/wait-for-it.sh", "db:5432", "--", "sh", "-c", ". venv/bin/activate && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]


