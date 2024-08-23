#!/bin/sh

# Wait for the database to be ready
/wait-for-it.sh db:5432

# Activate virtual environment
. venv/bin/activate

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Start Django server
python manage.py runserver 0.0.0.0:8000
