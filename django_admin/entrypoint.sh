#!/usr/bin/env sh
set -e

echo "==> Esperando a PostgreSQL en ${POSTGRES_HOST:-db}:5432..."
python initialize_con.py

echo "==> Aplicando migraciones..."
if ls django_admin/migrations/0*.py >/dev/null 2>&1; then
    echo " Eliminando migraciones anteriores ..."
    rm -f django_admin/migrations/0*.py
    touch django_admin/migrations/__init__.py
fi

echo " Creando nueva migración ..."
python manage.py makemigrations django_admin --noinput

echo " Aplicando migraciones ..."
python manage.py migrate --noinput

echo "==> Verificando dónde quedaron las tablas..."
python manage.py shell -c "
from django.db import connection
with connection.cursor() as c:
    c.execute(\"\"\"
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE tablename IN ('restaurantes','platos','pedido','item_pedido')
        ORDER BY schemaname, tablename;
    \"\"\")
    for row in c.fetchall():
        print(row)
"

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