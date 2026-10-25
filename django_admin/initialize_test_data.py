from django.db import connection, transaction

try:
    with open("data_test.sql", encoding="utf-8") as f:
        sql = f.read()

    with connection.cursor() as c:
        # Verificar si hay datos en la tabla (no si existe)
        c.execute("SELECT COUNT(*) FROM content.restaurantes;")
        if c.fetchone()[0] > 0:
            print("La tabla ya tiene datos, se omite la carga.")
        else:
            with transaction.atomic():
                c.execute(sql)
            print("Datos de prueba cargados.")

except Exception as e:
    print(f"Error al cargar datos: {e}")
    raise