#!/bin/sh
set -e

if [ "$1" = "runserver" ]; then
    cd demo
    python manage.py migrate --noinput
    python manage.py loaddata demo_content
    DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}" \
    DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-admin}" \
    DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" \
        python manage.py createsuperuser --noinput || true
    exec python manage.py runserver 0.0.0.0:8000
fi

exec "$@"
