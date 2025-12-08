import psycopg2
import os

# Usar la URL de Railway
DATABASE_URL = "postgresql://postgres:okWxjYLJuTNIpnAuwieahOcKrryCBcpt@switchyard.proxy.rlwy.net:21387/railway"

print("🔍 Intentando conectar a Railway...")
print(f"URL: {DATABASE_URL[:40]}...{DATABASE_URL[-20:]}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Prueba simple
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    
    print("✅ Conexión exitosa a Railway!")
    print(f"PostgreSQL version: {version[0]}")
    
    # Ver tablas existentes
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    tablas = cursor.fetchall()
    if tablas:
        print(f"\n📊 Tablas existentes: {len(tablas)}")
        for tabla in tablas:
            print(f"  - {tabla[0]}")
    else:
        print("\n📊 No hay tablas en la BD (vacía)")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error de conexión: {e}")
    print("\n💡 Verifica que:")
    print("  1. La URL sea correcta")
    print("  2. PostgreSQL esté instalado (pip install psycopg2-binary)")
    print("  3. Tengas acceso a Internet")
