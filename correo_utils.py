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


def _enviar_con_sendgrid(destinatario, asunto, html_content):
    """Envía correo usando SendGrid API"""
    try:
        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            logger.error("SENDGRID_API_KEY no está configurado")
            return False
        
        from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@agrimax.com')
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "personalizations": [{"to": [{"email": destinatario}]}],
            "from": {"email": from_email, "name": "AGRIMAX"},
            "subject": asunto,
            "content": [{"type": "text/html", "value": html_content}]
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 202:
            logger.info(f"Correo enviado exitosamente a {destinatario} via SendGrid")
            print(f"✓ Correo enviado a {destinatario} (SendGrid)")
            return True
        else:
            logger.error(f"Error SendGrid: {response.status_code} - {response.text}")
            print(f"✗ Error SendGrid: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error al enviar via SendGrid: {str(e)}")
        print(f"✗ Error SendGrid: {str(e)}")
        return False


def _enviar_con_resend(destinatario, asunto, html_content):
    """Envía correo usando Resend API (alternativa a Gmail)"""
    try:
        api_key = os.environ.get('RESEND_API_KEY')
        if not api_key:
            logger.error("RESEND_API_KEY no está configurado")
            return False
        
        # Email verificado del propietario de Resend
        resend_owner_email = os.environ.get('RESEND_OWNER_EMAIL', 'caph238@gmail.com')
        
        # En modo test de Resend, solo se puede enviar al propietario
        if destinatario.lower() != resend_owner_email.lower():
            logger.warning(f"Resend en modo test: no se puede enviar a {destinatario}. Solo se permite enviar a {resend_owner_email}.")
            logger.info(f"Para enviar a otros destinatarios, verifica un dominio en https://resend.com/domains")
            print(f"⚠️ Correo a {destinatario} no enviado: Resend requiere verificación de dominio para enviar a otros usuarios")
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
        
        # Prioridad 1: SendGrid (funciona sin verificación de dominio en plan gratuito)
        if os.environ.get('SENDGRID_API_KEY'):
            if _enviar_con_sendgrid(destinatario, asunto, html_content):
                return True
            logger.warning("SendGrid falló, intentando siguiente opción...")
        
        # Prioridad 2: Resend (requiere verificación de dominio para producción)
        if os.environ.get('RESEND_API_KEY'):
            resend_owner_email = os.environ.get('RESEND_OWNER_EMAIL', 'caph238@gmail.com')
            resultado = _enviar_con_resend(destinatario, asunto, html_content)
            if resultado:
                return True
            
            if destinatario.lower() != resend_owner_email.lower():
                logger.warning(f"⚠️ Resend en modo test: solo puede enviar a {resend_owner_email}")
        
        # Prioridad 3: Gmail SMTP (funciona localmente, bloqueado en Railway)
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
            logger.error(f"❌ No se pudo enviar correo a {destinatario}")
            logger.info(f"💡 Soluciones:")
            logger.info(f"   • Configura SENDGRID_API_KEY (recomendado): https://sendgrid.com/")
            logger.info(f"   • O verifica un dominio en Resend: https://resend.com/domains")
            print(f"❌ Correo NO enviado a {destinatario}")
            return False
            
    except Exception as e:
        logger.error(f"Error al enviar correo a {destinatario}: {str(e)}")
        print(f"✗ Error al enviar correo: {str(e)}")
        # NO hacer raise - retornar False
        return False


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
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo de pedido a {destinatario}: {str(e)}")
        print(f"✗ Error al enviar correo de pedido: {str(e)}")
        # NO hacer raise - solo retornar False
        return False


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
