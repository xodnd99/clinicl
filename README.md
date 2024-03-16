1-клонируем репеситори в pycharm https://github.com/ghostqaw/clinicl.git
2-активируем виртуальное окружение source venv/bin/activate
3-устанавливаем пакеты pip install -r requirements.txt
4-запишем изменения в файлы мирации находясь в корне проекта python manage.py makemigrations clinicApp  №перед применением миграции удалите файл 0001_initial.py в папке migrations/
5-применяем в файлы миграции python manage.py migrate
6-запуск проекта python manage.py runserver
7-создание суперпользователя python manage.py createsuperuser
8-откройте след адрес в браузере http://localhost:8000/admin/ и управляйте моделями 
