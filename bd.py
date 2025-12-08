import psycopg2
import os
from urllib.parse import urlparse

# Obtener DATABASE_URL de Railway o usar configuración local
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Usar DATABASE_URL de Railway
    configuracion_bd = database_url
else:
    # Configuración local para desarrollo
    configuracion_bd = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'database': os.environ.get('DB_NAME', 'AGRIMAX'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', '2812')
    }

# Función que retorna la conexión
def conectar_bd():
    try:
        if isinstance(configuracion_bd, str):
            # Conexión con DATABASE_URL (Railway)
            conexion = psycopg2.connect(configuracion_bd)
        else:
            # Conexión con diccionario (local)
            conexion = psycopg2.connect(**configuracion_bd)
        print("Conexión exitosa a la base de datos")
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Prueba local del módulo
if __name__ == "__main__":
    conectar_bd()