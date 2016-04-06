web: daphne logtacts.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker --settings=logtacts.prod_settings -v2