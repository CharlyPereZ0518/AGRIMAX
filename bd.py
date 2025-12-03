import psycopg2
import os

def conectar_bd():
    try:
        # Railway te da la URL completa en la variable de entorno
        database_url = os.environ.get("DATABASE_URL")

        # Conexión directa usando la URL
        conexion = psycopg2.connect(database_url)

        print("Conexión exitosa a la base de datos")
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Prueba local del módulo
if __name__ == "__main__":
    conectar_bd()