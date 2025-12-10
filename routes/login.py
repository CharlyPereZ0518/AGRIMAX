from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bd import conectar_bd
from flask_login import login_user
from models import Usuario
import bcrypt
import requests
import random
from datetime import datetime, timedelta
from correo_utils import enviar_correo
import re
import os

login_bp = Blueprint("login", __name__)

# Clave secreta de reCAPTCHA v3
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '6LcMNNsrAAAAAFj64Kr766S2lQLG5DkYYtnEFPDU')
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY', '6LcMNNsrAAAAAA...')

def verify_recaptcha_v3(token):
    """Verifica el token de reCAPTCHA v3 con Google"""
    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': RECAPTCHA_SECRET_KEY,
                'response': token
            },
            timeout=5
        )
        result = response.json()
        
        # reCAPTCHA v3 devuelve un score de 0.0 a 1.0
        # 1.0 = muy probablemente humano, 0.0 = muy probablemente bot
        if result.get('success') and result.get('score', 0) >= 0.5:
            return True, result.get('score', 0)
        return False, result.get('score', 0)
    except Exception as e:
        print(f"Error verificando reCAPTCHA: {e}")
        return False, 0.0

@login_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')
        recaptcha_token = request.form.get('g-recaptcha-response')

        if not correo or not contraseña:
            flash("Debes ingresar correo y contraseña.", "error")
            return render_template('login.html', site_key=RECAPTCHA_SITE_KEY)

        # Verificar reCAPTCHA v3
        if recaptcha_token:
            is_valid, score = verify_recaptcha_v3(recaptcha_token)
            if not is_valid:
                flash(f"Verificación de seguridad fallida. Por favor intenta nuevamente.", "error")
                return render_template('login.html', site_key=RECAPTCHA_SITE_KEY)
            print(f"reCAPTCHA score: {score}")
        else:
            flash("Verificación de seguridad requerida.", "error")
            return render_template('login.html', site_key=RECAPTCHA_SITE_KEY)

        try:
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT id, nombre, tipo, contraseña FROM usuarios WHERE correo = %s
                """, (correo,))
                usuario = cursor.fetchone()
                cursor.close()
                conexion.close()

                if usuario and usuario[3] and bcrypt.checkpw(contraseña.encode('utf-8'), usuario[3].encode('utf-8')):
                    # Si es admin, permitir login directo sin verificación
                    if usuario[2] == 'admin':
                        user_obj = Usuario(usuario[0], usuario[1], usuario[2])
                        login_user(user_obj)
                        session['usuario_id'] = usuario[0]
                        session['usuario_nombre'] = usuario[1]
                        session['usuario_tipo'] = usuario[2]
                        flash("Inicio de sesión exitoso.", "success")
                        return redirect(url_for('admin_dashboard.admin_dashboard'))
                    
                    # Para otros usuarios, generar código de verificación
                    codigo = '{:06d}'.format(random.randint(0, 999999))
                    expires_at = (datetime.utcnow() + timedelta(minutes=5)).timestamp()
                    session['2fa_pending'] = {
                        'user_id': usuario[0],
                        'nombre': usuario[1],
                        'tipo': usuario[2],
                        'correo': correo,
                        'code': codigo,
                        'expires': expires_at
                    }

                    # Enviar correo con el código de verificación
                    try:
                        enviar_correo(correo, "Código de verificación AGRIMAX", 'correo_verificacion.html', {"nombre": usuario[1], "codigo": codigo})
                        flash("Se ha enviado un código de verificación a tu correo.", "info")
                    except Exception as e:
                        print("Error al enviar código de verificación:", str(e))
                        flash(f"Error al enviar el código: {str(e)}", "error")
                        return render_template('login.html')
                    return redirect(url_for('verificar_codigo.verificar_codigo'))
                else:
                    flash("Correo o contraseña incorrectos.", "error")
                    return render_template('login.html', site_key=RECAPTCHA_SITE_KEY)
            else:
                flash("Error al conectar con la base de datos.", "error")
                return render_template('login.html', site_key=RECAPTCHA_SITE_KEY)
        except Exception as e:
            print("Error al iniciar sesión:", e)
            flash("Ocurrió un error al iniciar sesión. Intenta nuevamente.", "error")
            return render_template('login.html', site_key=RECAPTCHA_SITE_KEY)

    return render_template('login.html', site_key=RECAPTCHA_SITE_KEY)