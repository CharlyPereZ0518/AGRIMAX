#!/usr/bin/env python3
"""
Script para probar la conexión y envío de correos desde Railway
"""
import os
import sys
from app import app, mail
from flask_mail import Message

def test_mail_config():
    """Verificar configuración de correo"""
    print("=" * 60)
    print("PRUEBA DE CONFIGURACIÓN DE CORREO")
    print("=" * 60)
    
    with app.app_context():
        config = {
            'MAIL_SERVER': app.config.get('MAIL_SERVER'),
            'MAIL_PORT': app.config.get('MAIL_PORT'),
            'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
            'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
            'MAIL_PASSWORD': '***' + app.config.get('MAIL_PASSWORD', '')[-4:] if app.config.get('MAIL_PASSWORD') else 'NO CONFIGURADO'
        }
        
        for key, value in config.items():
            print(f"{key}: {value}")
        
        print("\n" + "=" * 60)
        print("INTENTANDO ENVIAR CORREO DE PRUEBA")
        print("=" * 60)
        
        try:
            msg = Message(
                subject="Prueba de AGRIMAX",
                sender=app.config.get('MAIL_USERNAME'),
                recipients=["agrimaaxx@gmail.com"],
                body="Este es un correo de prueba desde Railway"
            )
            mail.send(msg)
            print("\n✓ ¡Correo enviado exitosamente!")
            return True
        except Exception as e:
            print(f"\n✗ Error al enviar correo:")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")
            import traceback
            print("\nStack trace completo:")
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_mail_config()
    sys.exit(0 if success else 1)
