from flask import render_template, current_app
from flask_mail import Message
from extensions import mail
import logging
import socket
import os
import requests

# Configurar logging para ver errores de correo
logger = logging.getLogger(__name__)


def _check_network():
    """Verifica conectividad de red a Gmail"""
    try:
        socket.create_connection(('smtp.gmail.com', 587), timeout=5)
        return True
    except (socket.timeout, socket.gaierror, OSError) as e:
        logger.error(f"Error de conectividad de red: {str(e)}")
        return False


def _enviar_con_resend(destinatario, asunto, html_content):
    """Envía correo usando Resend API (alternativa a Gmail)"""
    try:
        api_key = os.environ.get('RESEND_API_KEY')
        if not api_key:
            logger.error("RESEND_API_KEY no está configurado")
            return False
        
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": "Agrimax <noreply@resend.dev>",
            "to": destinatario,
            "subject": asunto,
            "html": html_content
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Correo enviado exitosamente a {destinatario} via Resend")
            print(f"✓ Correo enviado a {destinatario} (Resend)")
            return True
        else:
            logger.error(f"Error Resend: {response.status_code} - {response.text}")
            print(f"✗ Error Resend: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error al enviar via Resend: {str(e)}")
        print(f"✗ Error Resend: {str(e)}")
        return False


def enviar_correo(destinatario, asunto, plantilla, datos):
    try:
        # Renderizar el HTML
        html_content = render_template(plantilla, datos=datos)
        
        # Intentar primero con Resend (recomendado para Railway)
        if os.environ.get('RESEND_API_KEY'):
            if _enviar_con_resend(destinatario, asunto, html_content):
                return True
            else:
                logger.warning("Resend falló, intentando con Gmail...")
        
        # Fallback a Gmail SMTP
        try:
            mensaje = Message(
                asunto,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[destinatario]
            )
            mensaje.html = html_content
            mail.send(mensaje)
            logger.info(f"Correo enviado exitosamente a {destinatario} via Gmail")
            print(f"✓ Correo enviado a {destinatario} (Gmail)")
            return True
        except Exception as smtp_error:
            logger.error(f"Error Gmail SMTP: {str(smtp_error)}")
            logger.info("Intenta configurar RESEND_API_KEY en Railway para mejor compatibilidad")
            raise
            
    except Exception as e:
        logger.error(f"Error al enviar correo a {destinatario}: {str(e)}")
        print(f"✗ Error al enviar correo: {str(e)}")
        raise


def enviar_correo_pedido(destinatario, pedido_id, total, productos):
    try:
        # Renderizar HTML
        html_content = render_template(
            'correo_pedido.html',
            datos={"pedido_id": pedido_id, "total": total, "productos": productos}
        )
        
        # Intentar con Resend primero
        if os.environ.get('RESEND_API_KEY'):
            if _enviar_con_resend(destinatario, "Confirmación de Pedido", html_content):
                return True
        
        # Fallback a Gmail
        mensaje = Message(
            "Confirmación de Pedido",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[destinatario]
        )
        mensaje.html = html_content
        mail.send(mensaje)
        logger.info(f"Correo de pedido enviado a {destinatario}")
        print(f"✓ Correo de pedido enviado a {destinatario}")
    except Exception as e:
        logger.error(f"Error al enviar correo de pedido a {destinatario}: {str(e)}")
        print(f"✗ Error al enviar correo de pedido: {str(e)}")
        raise


def enviar_correo_registro(destinatario, nombre, tipo_usuario):
    try:
        if tipo_usuario == "Cliente":
            asunto = "¡Bienvenido a AGRIMAX!"
            plantilla = "correo_cliente.html"
        elif tipo_usuario == "Proveedor":
            asunto = "¡Bienvenido a AGRIMAX, proveedor!"
            plantilla = "correo_proveedor.html"
        else:
            return

        html_content = render_template(plantilla, datos={"nombre": nombre})
        
        # Intentar con Resend primero
        if os.environ.get('RESEND_API_KEY'):
            if _enviar_con_resend(destinatario, asunto, html_content):
                return
        
        # Fallback a Gmail
        mensaje = Message(
            asunto,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[destinatario]
        )
        mensaje.html = html_content
        mail.send(mensaje)
        logger.info(f"Correo de registro enviado a {destinatario}")
        print(f"✓ Correo de registro enviado a {destinatario}")
    except Exception as e:
        logger.error(f"Error al enviar correo de registro a {destinatario}: {str(e)}")
        print(f"✗ Error al enviar correo de registro: {str(e)}")
