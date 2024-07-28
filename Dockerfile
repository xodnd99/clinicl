FROM python:3.12

RUN apt-get update && apt-get install -y cmake
RUN pip install --upgrade pip

WORKDIR /app

COPY . /app

RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

RUN . venv/bin/activate && python manage.py makemigrations clinicApp && python manage.py migrate

EXPOSE 8000

CMD ["sh", "-c", ". venv/bin/activate && python manage.py runserver 0.0.0.0:8000"]



