Minimal Alexie

Superuser: heitor/d-----##

Ubuntu setup
One-time only in /minialexie folder:
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate

(only once) pip install Django

(only once) python manage.py migrate
(only once) python manage.py createsuperuser

alexie - first version. Stopped development on 24.nov.16

benny - second version. Began development on 24.nov.16

> python manage.py runserver
