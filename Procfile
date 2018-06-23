web: gunicorn teamexchange.wsgi --log-file -

web: gunicorn --pythonpath="$PWD/teamexchange" config.wsgi:application

worker: python teamexchange/manage.py rqworker high default low
