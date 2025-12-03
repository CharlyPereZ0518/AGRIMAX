import psycopg2
import os

def cargar_sql():
    try:
        # Conexión usando la variable de entorno DATABASE_URL
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cur = conn.cursor()

        # Abrimos el archivo SQL y lo ejecutamos línea por línea
        with open("C:/Users/Beto/Desktop/AGRIMAX.SQL", "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Ejecutar todo el script
        cur.execute(sql_script)

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Base de datos cargada en Railway correctamente")

    except Exception as e:
        print(f"❌ Error al cargar la base de datos: {e}")

if __name__ == "__main__":
    cargar_sql()