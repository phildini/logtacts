web: gunicorn logtacts.wsgi -v2 --log-file -
worker: python manage.py runworker --settings=logtacts.prod_settings -v2