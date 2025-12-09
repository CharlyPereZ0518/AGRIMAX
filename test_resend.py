#!/usr/bin/env python3
"""
Script para probar el envío de correos con Resend en Railway
"""
import os
import sys
import requests
from app import app

def test_resend():
    """Prueba la configuración de Resend"""
    print("=" * 60)
    print("PRUEBA DE RESEND PARA RAILWAY")
    print("=" * 60)
    
    api_key = os.environ.get('RESEND_API_KEY')
    
    if not api_key:
        print("\n✗ RESEND_API_KEY no está configurado")
        print("\nPasos para configurarlo:")
        print("1. Ve a https://resend.com y regístrate (gratis)")
        print("2. Ve a API Keys")
        print("3. Copia tu API Key")
        print("4. En Railway, agrega: RESEND_API_KEY=tu_api_key")
        return False
    
    print(f"\n✓ RESEND_API_KEY detectado: {api_key[:10]}...")
    
    print("\n" + "=" * 60)
    print("ENVIANDO CORREO DE PRUEBA")
    print("=" * 60)
    
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": "Agrimax <noreply@resend.dev>",
            "to": "agrimaaxx@gmail.com",
            "subject": "Prueba de AGRIMAX desde Resend",
            "html": """
            <h2>¡Hola!</h2>
            <p>Este es un correo de prueba desde Resend.</p>
            <p>Si lo recibiste, significa que Resend está funcionando correctamente en Railway.</p>
            <p>- AGRIMAX</p>
            """
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"\nCódigo de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ ¡Correo enviado exitosamente!")
            print(f"  Email ID: {data.get('id')}")
            return True
        else:
            print(f"✗ Error al enviar:")
            print(f"  {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_resend()
    
    if not success:
        print("\n" + "=" * 60)
        print("SOLUCIÓN RÁPIDA:")
        print("=" * 60)
        print("Usa Resend en lugar de Gmail SMTP:")
        print("1. https://resend.com (regístrate gratis)")
        print("2. Copia tu API Key")
        print("3. En Railway Settings > Variables:")
        print("   RESEND_API_KEY=tu_api_key")
        print("4. Deploy nuevamente")
        print("=" * 60)
    
    sys.exit(0 if success else 1)
