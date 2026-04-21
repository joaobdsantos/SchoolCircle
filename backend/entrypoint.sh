#!/bin/sh
set -e

python - <<'PY'
import os
import time

import psycopg2


params = {
    "dbname": os.getenv("POSTGRES_DB", "school_circle"),
    "user": os.getenv("POSTGRES_USER", "school_circle"),
    "password": os.getenv("POSTGRES_PASSWORD", "school_circle"),
    "host": os.getenv("POSTGRES_HOST", "db"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

for attempt in range(30):
    try:
        connection = psycopg2.connect(**params)
        connection.close()
        break
    except psycopg2.OperationalError:
        time.sleep(1)
else:
    raise SystemExit("Database is unavailable after waiting.")
PY

python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
