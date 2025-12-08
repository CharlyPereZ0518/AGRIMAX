import psycopg2
import os
from pathlib import Path

def cargar_sql(archivo_sql=None):
    try:
        # Obtener DATABASE_URL de Railway
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL no está configurada")
            return False

        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Determinar la ruta del archivo SQL
        if not archivo_sql:
            # Buscar AGRIMAX.sql en el directorio actual o raíz del proyecto
            posibles_rutas = [
                Path("AGRIMAX.sql"),
                Path(__file__).parent / "AGRIMAX.sql",
                Path("C:/Users/Beto/Desktop/AGRIMAX.SQL"),  # Fallback
            ]
            
            archivo_sql = None
            for ruta in posibles_rutas:
                if ruta.exists():
                    archivo_sql = str(ruta)
                    break
        
        if not archivo_sql or not Path(archivo_sql).exists():
            print(f"❌ No se encontró el archivo SQL en las rutas esperadas")
            return False

        print(f"📂 Leyendo archivo: {archivo_sql}")
        
        with open(archivo_sql, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Dividir el script por ';' y ejecutar sentencia por sentencia
        sentencias = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        for i, sentencia in enumerate(sentencias, 1):
            try:
                cur.execute(sentencia)
                conn.commit()  # commit por sentencia para evitar que un fallo bloquee todo
                print(f"✓ Sentencia {i}/{len(sentencias)} ejecutada")
            except Exception as e:
                # Hacer rollback de la sentencia fallida para limpiar el estado de la conexión
                try:
                    conn.rollback()
                except Exception:
                    pass
                print(f"⚠ Error en sentencia {i}: {e}")
                # Continuar con las siguientes sentencias
                continue

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Base de datos cargada en Railway correctamente")
        return True

    except Exception as e:
        print(f"❌ Error al cargar la base de datos: {e}")
        return False

if __name__ == "__main__":
    cargar_sql()