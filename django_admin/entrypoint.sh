#!/usr/bin/env sh
set -e

echo "==> Esperando a PostgreSQL en ${POSTGRES_HOST:-db}:5432..."
python - <<'PY'
import os, sys, time
import psycopg

host = os.environ.get("POSTGRES_HOST")
user = os.environ["POSTGRES_USER"]
pwd  = os.environ["POSTGRES_PASSWORD"]
db   = os.environ["POSTGRES_DB"]

for i in range(30):
    try:
        psycopg.connect(host=host, user=user, password=pwd, dbname=db, connect_timeout=2).close()
        print("    ✔ PostgreSQL listo")
        sys.exit(0)
    except Exception as e:
        print(f"    ... intento {i+1}/30: {e}")
        time.sleep(2)
print("    ✘ No se pudo conectar a PostgreSQL", file=sys.stderr)
sys.exit(1)
PY

echo "==> Aplicando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "==> Recolectando estáticos..."
python manage.py collectstatic --noinput || true

echo "==> Arrancando Gunicorn..."
exec "$@"