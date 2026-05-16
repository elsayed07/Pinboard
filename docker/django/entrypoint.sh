#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "
import os, sys, psycopg
try:
    psycopg.connect(
        host=os.environ.get('DB_HOST', 'db'),
        port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ.get('POSTGRES_DB', 'pinboard'),
        user=os.environ.get('POSTGRES_USER', 'pinboard'),
        password=os.environ.get('POSTGRES_PASSWORD', 'pinboard'),
    )
except Exception as e:
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
done
echo "Database ready."

uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput --clear

exec "$@"
