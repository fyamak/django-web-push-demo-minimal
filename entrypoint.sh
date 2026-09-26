#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py ensure_vapid_keys

if [ "${1:-local}" = "test" ]; then
  python manage.py collectstatic --noinput
  exec gunicorn pushdemo.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60
fi

exec python manage.py runserver 0.0.0.0:8000
