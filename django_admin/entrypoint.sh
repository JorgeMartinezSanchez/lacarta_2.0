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
python manage.py shell < initialize_test_data.py

echo "==> Arrancando Gunicorn..."
exec "$@"