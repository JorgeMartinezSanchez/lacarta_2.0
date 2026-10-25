#!/usr/bin/env sh
set -e

echo "==> Esperando a PostgreSQL en ${POSTGRES_HOST:-db}:5432..."
python initialize_con.py

echo "==> Aplicando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "==> Creando cuenta admin de Django:"
echo "Username: ${DJANGO_SUPERUSER_USERNAME}"
echo "Email: ${DJANGO_SUPERUSER_EMAIL}"
echo "Password: ${DJANGO_SUPERUSER_PASSWORD}"

python manage.py createsuperuser --noinput 2>/dev/null || echo "Superusuario ya existe, se omite."

echo "==> Recolectando estáticos..."
python manage.py collectstatic --noinput || true

echo "==> Inicializando datos de prueba..."
python manage.py shell <<'EOF'
from django.db import connection
with connection.cursor() as c:
    c.execute("SELECT COUNT(*) FROM content.restaurantes")
    if c.fetchone()[0] == 0:
        c.execute(open("data_test.sql", encoding="utf-8").read())
        print("Datos de prueba cargados.")
    else:
        print("La tabla ya tiene datos, se omite la carga.")
EOF

echo "==> Arrancando Gunicorn..."
exec "$@"