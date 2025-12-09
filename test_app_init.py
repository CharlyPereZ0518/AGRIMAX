"""
Script para probar si app.py se puede importar correctamente
"""
import sys
import os

print("=" * 60)
print("Test de inicialización de la aplicación")
print("=" * 60)

try:
    print("\n1. Intentando importar app...")
    from app import app
    print("   ✅ app importado correctamente")
    
    print("\n2. Verificando configuración básica...")
    print(f"   - SECRET_KEY configurada: {bool(app.secret_key)}")
    print(f"   - Blueprints registrados: {len(app.blueprints)}")
    
    print("\n3. Listando blueprints registrados:")
    for name in sorted(app.blueprints.keys()):
        print(f"   - {name}")
    
    print("\n4. Verificando rutas disponibles:")
    route_count = len(list(app.url_map.iter_rules()))
    print(f"   - Total de rutas: {route_count}")
    
    print("\n" + "=" * 60)
    print("✅ LA APLICACIÓN SE PUEDE INICIALIZAR CORRECTAMENTE")
    print("=" * 60)
    
except ImportError as e:
    print(f"\n❌ ERROR DE IMPORTACIÓN:")
    print(f"   {e}")
    print("\n   Posibles causas:")
    print("   - Falta instalar alguna dependencia")
    print("   - Archivo de ruta faltante o con errores")
    import traceback
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR AL INICIALIZAR:")
    print(f"   {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
