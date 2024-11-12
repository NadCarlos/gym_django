# #!/bin/sh

cd gym

service cron start
python3 manage.py crontab add

sleep 10

python3 manage.py migrate
python3 manage.py collectstatic --noinput --clear
python3 manage.py runserver 0.0.0.0:8000
