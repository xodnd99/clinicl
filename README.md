Attention: Для корректной работы вам нужна установленная ОС Ubuntu или любая другая виртуальная машина на базе Ubuntu

1-клонируем репеситори в pycharm https://github.com/ghostqaw/clinicl.git

2-активируем виртуальное окружение source venv/bin/activate

3-устанавливаем пакеты pip install -r requirements.txt
возможно при установке зависымых пакетов появится ошибка установки blib, для решения запустите команду sudo apt install cmake

4-установка и настройка БД Postgresql для установки выполните след команды sudo apt update sudo apt install postgresql, запустите БД по команде sudo systemctl start postgresql 
Потом войдите в интерактивную среду БД по команде sudo -u postgres psql, установите пароль для пользвателя postgres по команде ALTER USER postgres WITH PASSWORD 'qaz123'; 
p.s пароль желательно не менять, иначе придется переконфигурировать подключение БД в файле settings.py
![image](https://github.com/user-attachments/assets/8f164549-0376-4da4-a5fd-652ba1d06166)

 

5-запишем изменения в файл мирации находясь в корне проекта python manage.py makemigrations clinicApp  перед применением миграции удалите все файлы миграции кроме  __init__.py в папке clinicApp/migrations/

6-применяем в файлы миграции python manage.py migrate

7-запуск проекта python manage.py runserver

8-создание суперпользователя python manage.py createsuperuser

9-откройте след адрес в браузере http://localhost:8000/admin/ и управляйте моделями 
