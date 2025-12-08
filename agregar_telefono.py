import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://postgres:okWxjYLJuTNIpnAuwieahOcKrryCBcpt@switchyard.proxy.rlwy.net:21387/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("🔍 Verificando estructura actual de usuarios...")
    # Obtener columnas existentes
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'usuarios'
    """)
    
    columnas = cur.fetchall()
    print("\n📊 Columnas actuales en 'usuarios':")
    for col_name, data_type in columnas:
        print(f"  - {col_name} ({data_type})")
    
    # Verificar si la columna telefono ya existe
    col_names = [col[0] for col in columnas]
    
    if 'telefono' not in col_names:
        print("\n➕ Agregando columna 'telefono' a la tabla usuarios...")
        cur.execute("ALTER TABLE usuarios ADD COLUMN telefono VARCHAR(20) NOT NULL DEFAULT ''")
        conn.commit()
        print("✅ Columna 'telefono' agregada exitosamente")
    else:
        print("\n⚠️ La columna 'telefono' ya existe en la tabla usuarios")
    
    cur.close()
    conn.close()
    print("\n✅ Operación completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
