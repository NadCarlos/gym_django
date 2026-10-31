# #!/bin/sh

# CVE-2026-84243 requires an attacker-controlled LANGUAGE traversal. Keep the
# application locale fixed before starting cron, Django commands or Gunicorn.
export LANG=es_AR.UTF-8
export LANGUAGE=es_AR:es
export LC_ALL=es_AR.UTF-8

cd gym

service cron start
python3 manage.py crontab add

sleep 10

python3 manage.py migrate
python3 manage.py collectstatic --noinput --clear

echo "Starting Gunicorn..."
exec gunicorn \
  --bind 0.0.0.0:8000 \
  --worker-class gthread \
  --workers 2 \
  --threads 4 \
  --timeout 60 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --max-requests 500 \
  --max-requests-jitter 50 \
  --worker-tmp-dir /dev/shm \
  --access-logfile - \
  --error-logfile - \
  gym.wsgi:application
