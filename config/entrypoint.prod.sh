# #!/bin/sh

cd gym

service cron start
python3 manage.py crontab add

sleep 10

python3 manage.py migrate
python3 manage.py collectstatic --noinput --clear

echo "Starting Gunicorn..."
exec gunicorn --workers 3 --timeout=120 --bind 0.0.0.0:8000 gym.wsgi:application