web: gunicorn teamexchange.wsgi --log-file -

#web: gunicorn --pythonpath="$PWD/teamexchange" config.wsgi:application

worker: python manage.py rqworker default
