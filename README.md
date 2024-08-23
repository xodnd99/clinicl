проект можно скопировать и запустить в среде разработки PyCharm или прямо в терминале  BASH 
Attention: Для корректной работы вам нужна установленная ОС Ubuntu или любая другая виртуальная машина на базе Ubuntu
Advice: Если вы работаете в ОС Windows советую вам просто установить Windows Subsystem for Linux (WSL) для быстрого запуска 

Шаги запуска:
1-клонируем репеситори в pycharm https://github.com/ghostqaw/clinicl.git

2-активируем виртуальное окружение source venv/bin/activate

3-устанавливаем пакеты pip install -r requirements.txt
возможно при установке зависымых пакетов появится ошибка установки blib, для решения запустите команду sudo apt install cmake

4-установка и настройка БД Postgresql для установки выполните след командуы: sudo apt update sudo && apt install postgresql, запустите БД по команде sudo systemctl start postgresql. 
Потом войдите в интерактивную среду БД по команде: sudo -u postgres psql, установите пароль для пользвателя postgres по команде: ALTER USER postgres WITH PASSWORD 'qaz123'; 
p.s пароль желательно не менять, иначе придется переконфигурировать подключение к БД в файле settings.py


![image](https://github.com/user-attachments/assets/8f164549-0376-4da4-a5fd-652ba1d06166)

 

5-запишем изменения в файл мирации находясь в корне проекта python manage.py makemigrations clinicApp  перед применением миграции удалите все файлы миграции кроме  __init__.py в папке clinicApp/migrations/

6-применяем в файлы миграции python manage.py migrate

7-запуск проекта python manage.py runserver

8-создание суперпользователя python manage.py createsuperuser

9-откройте след адрес в браузере https://0.0.0.0:8000/admin/ если не сутановлены SSL сертификаты просто откройте ссылку https://0.0.0.0:8000/admin/ для доступа к панели администратора 


Чтобы развернуть все на новой машине выполните команду: docker-compose up --build

Эта команда создаст образы Docker и запустит контейнеры, автоматически выполнив миграцию и запустив приложение.




------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


the project can be copied and run in the PyCharm development environment or directly in the BASH terminal
Attention: For correct operation, you need an installed Ubuntu OS or any other Ubuntu-based virtual machine
Advice: If you are working in Windows, I advise you to simply install the Windows Subsystem for Linux (WSL) for a quick start

Launch steps:
1-clone the repositories in pycharm https://github.com/ghostqaw/clinicl.git

2-activate the virtual environment source venv/bin/activate

3-install packages pip install -r requirements.txt
maybe when installing dependent packages, an error will appear installing blib, to solve it, run the command sudo apt install cmake

4-install and configure the Postgresql database to install, run the following command sudo apt update sudo apt install postgresql, start the database with the command sudo systemctl start postgresql
Then enter the interactive database environment with the command sudo -u postgres psql, set password for user postgres with command ALTER USER postgres WITH PASSWORD 'qaz123'; p.s. it is advisable not to change the password, otherwise you will have to reconfigure the database connection in the settings.py file

![image](https://github.com/user-attachments/assets/8f164549-0376-4da4-a5fd-652ba1d06166)

5-write the changes to the migration file while in the root of the project python manage.py makemigrations clinicApp before applying the migration, delete all migration files except __init__.py in the clinicApp/migrations/ folder

6-apply to the migration files python manage.py migrate

7-run the project python manage.py runserver

8-create a superuser python manage.py createsuperuser

9-open the following address in the browser https://0.0.0.0:8000/admin/ and manage the models


To deploy everything on a new machine, run the command: docker-compose up --build

This command will create Docker images and launch containers, automatically migrating and running the application.
