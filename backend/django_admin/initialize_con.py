import os, sys, time
import psycopg

host = os.environ.get("POSTGRES_HOST")
user = os.environ["POSTGRES_USER"]
pwd  = os.environ["POSTGRES_PASSWORD"]
db   = os.environ["POSTGRES_DB"]

for i in range(30):
    try:
        with psycopg.connect(host=host, user=user, password=pwd, dbname=db, connect_timeout=2) as conn:
            print("    ✔ PostgreSQL listo")
            with conn.cursor() as cur:
                print(' Creando esquema "content" ... ')
                cur.execute("CREATE SCHEMA IF NOT EXISTS content AUTHORIZATION CURRENT_USER;")
                print('     ✔ Esquema "content" creado')
            # al salir del with, se hace commit automáticamente
        sys.exit(0)
    except Exception as e:
        print(f"    ... intento {i+1}/30: {e}")
        time.sleep(2)

print('    ✘ No se pudo conectar a PostgreSQL o crear el esquema "content"', file=sys.stderr)
sys.exit(1)