import psycopg2
import os
from urllib.parse import urlparse

# Obtener DATABASE_URL de Railway o usar configuración local
database_url = os.environ.get("DATABASE_URL")

def _mask_db_url(url):
    try:
        # enmascara la contraseña si existe: postgresql://user:pass@host:port/db -> postgresql://user:*****@host:port/db
        if not url:
            return None
        if '@' in url and '://' in url:
            prefix, rest = url.split('://', 1)
            if ':' in rest and '@' in rest:
                userinfo, hostpart = rest.split('@', 1)
                if ':' in userinfo:
                    user, _pass = userinfo.split(':', 1)
                    return f"{prefix}://{user}:*****@{hostpart}"
        return url
    except Exception:
        return '***'

if database_url:
    # Usar DATABASE_URL de Railway
    configuracion_bd = database_url
    print(f"[bd] Usando DATABASE_URL: {_mask_db_url(database_url)}")
else:
    # Configuración local para desarrollo
    configuracion_bd = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'database': os.environ.get('DB_NAME', 'AGRIMAX'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', '2812')
    }
    print(f"[bd] Usando conexión local: host={configuracion_bd['host']}, database={configuracion_bd['database']}")

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