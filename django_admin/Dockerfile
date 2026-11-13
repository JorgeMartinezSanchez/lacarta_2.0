FROM python:3.14-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x ./entrypoint.sh

EXPOSE 8000

# Producción: este contenedor solo sirve el admin.
# Migraciones, superusuario, collectstatic y datos de prueba los hace el
# servicio "migrate" de docker-compose.yml (ejecuta ./entrypoint.sh y termina).
CMD ["gunicorn", "django_admin.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
