import psycopg2

# Diccionario con los datos de conexión
configuracion_bd = {
    'host': 'localhost',
    'database': 'AGRIMAX',
    'user': 'postgres',
    'password': '12345',
    
}

# Función que retorna la conexión
def conectar_bd():
    try:
        conexion = psycopg2.connect(**configuracion_bd)
        print("✅ Conexión exitosa a la base de datos")
        return conexion
    except psycopg2.Error as e:
        print("❌ Error de psycopg2:", e.pgerror or str(e))
    except Exception as e:
        print("⚠️ Error general al conectar:", str(e))
    return None

# Prueba local del módulo
if __name__ == "__main__":
    conn = conectar_bd()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                print("Versión de PostgreSQL:", cur.fetchone()[0])
        finally:
            conn.close()