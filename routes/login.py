from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bd import conectar_bd
from flask_login import login_user
from models import Usuario
import bcrypt
import requests
import random
from datetime import datetime, timedelta
from correo_utils import enviar_correo

login_bp = Blueprint("login", __name__)

# Clave secreta de reCAPTCHA (reemplaza con la tuya)
RECAPTCHA_SECRET_KEY = '6LcMNNsrAAAAAFj64Kr766S2lQLG5DkYYtnEFPDU'

@login_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')
        captcha_response = request.form.get('g-recaptcha-response')

        if not correo or not contraseña:
            flash("Debes ingresar correo y contraseña.", "error")
            return render_template('login.html')

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
                    # Generar código de verificación y guardarlo en sesión temporal
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
                    except Exception as e:
                        print("Error al enviar código de verificación:", e)

                    flash("Se ha enviado un código de verificación a tu correo.", "info")
                    return redirect(url_for('verificar_codigo.verificar_codigo'))
                else:
                    flash("Correo o contraseña incorrectos.", "error")
                    return render_template('login.html')
            else:
                flash("Error al conectar con la base de datos.", "error")
                return render_template('login.html')
        except Exception as e:
            print("Error al iniciar sesión:", e)
            flash("Ocurrió un error al iniciar sesión. Intenta nuevamente.", "error")
            return render_template('login.html')

    return render_template('login.html')