#!/bin/sh
# Only the isolated rehearsal database may be mutated by this script.
set -eu
if [ "${MYSQL_HOST:-}" != db84 ] || [ "${MYSQL_DATABASE:-}" != cermed_rehearsal ]; then
    echo 'Refusing to run migrations/tests outside the isolated rehearsal.' >&2
    exit 2
fi
python -m pip check
python gym/manage.py check
python gym/manage.py makemigrations --check --dry-run
python gym/manage.py migrate --plan
python gym/manage.py migrate --noinput
python gym/manage.py migrate --check
python gym/manage.py test administracion rehabilitacion finanzas entrada usuarios home --noinput
python gym/manage.py collectstatic --dry-run --noinput
python gym/manage.py check --deploy
