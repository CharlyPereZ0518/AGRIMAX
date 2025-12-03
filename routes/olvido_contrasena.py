from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bd import conectar_bd
from correo_utils import enviar_correo
import random
from datetime import datetime, timedelta
import bcrypt
import re

olvido_bp = Blueprint('olvido_contrasena', __name__)


@olvido_bp.route('/olvido_contrasena', methods=['GET', 'POST'])
def solicitar_reset():
    if request.method == 'POST':
        correo = request.form.get('correo')
        if not correo:
            flash('Ingresa tu correo.', 'error')
            return render_template('olvido_contrasena.html')

        try:
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT id, nombre FROM usuarios WHERE correo = %s", (correo,))
                usuario = cursor.fetchone()
                cursor.close()
                conexion.close()

                if not usuario:
                    flash('No existe una cuenta con ese correo.', 'error')
                    return render_template('olvido_contrasena.html')

                # generar código y guardar en sesión
                codigo = '{:06d}'.format(random.randint(0, 999999))
                expires_at = (datetime.utcnow() + timedelta(minutes=15)).timestamp()
                session['pw_reset_pending'] = {
                    'user_id': usuario[0],
                    'nombre': usuario[1],
                    'correo': correo,
                    'code': codigo,
                    'expires': expires_at
                }

                # enviar correo de restablecimiento
                try:
                    enviar_correo(correo, 'Restablece tu contraseña - AGRIMAX', 'correo_reset.html', {"nombre": usuario[1], "codigo": codigo})
                except Exception as e:
                    print('Error al enviar correo de restablecimiento:', e)

                flash('Se ha enviado un correo con instrucciones para restablecer tu contraseña.', 'info')
                return redirect(url_for('olvido_contrasena.reset_password'))
            else:
                flash('Error al conectar con la base de datos.', 'error')
                return render_template('olvido_contrasena.html')
        except Exception as e:
            print('Error en solicitud de reset:', e)
            flash('Ocurrió un error. Intenta nuevamente.', 'error')
            return render_template('olvido_contrasena.html')

    return render_template('olvido_contrasena.html')


@olvido_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    pending = session.get('pw_reset_pending')
    if not pending:
        flash('No hay un proceso de restablecimiento activo. Solicítalo primero.', 'error')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nueva = request.form.get('contraseña')
        confirmar = request.form.get('confirmar')

        if not codigo or not nueva or not confirmar:
            flash('Completa todos los campos.', 'error')
            return render_template('reset_password.html')

        if nueva != confirmar:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('reset_password.html')

        # Validar que la nueva contraseña tenga al menos un número y un carácter especial
        if not re.search(r"(?=.*\d)(?=.*[^A-Za-z0-9])", nueva):
            flash('La contraseña debe contener al menos un número y un carácter especial.', 'error')
            return render_template('reset_password.html')

        try:
            expires_ts = float(pending.get('expires', 0))
        except Exception:
            expires_ts = 0

        from datetime import datetime
        if datetime.utcnow().timestamp() > expires_ts:
            session.pop('pw_reset_pending', None)
            flash('El código ha expirado. Solicita nuevamente restablecer la contraseña.', 'error')
            return redirect(url_for('olvido_contrasena.solicitar_reset'))

        if codigo != pending.get('code'):
            flash('Código incorrecto.', 'error')
            return render_template('reset_password.html')

        # actualizar contraseña en la base de datos
        try:
            hashed = bcrypt.hashpw(nueva.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("UPDATE usuarios SET contraseña = %s WHERE id = %s", (hashed, pending.get('user_id')))
                conexion.commit()
                cursor.close()
                conexion.close()

                session.pop('pw_reset_pending', None)
                flash('Contraseña actualizada correctamente. Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('login.login'))
            else:
                flash('Error al conectar con la base de datos.', 'error')
                return render_template('reset_password.html')
        except Exception as e:
            print('Error al actualizar contraseña:', e)
            flash('Ocurrió un error al actualizar la contraseña.', 'error')
            return render_template('reset_password.html')

    return render_template('reset_password.html')
