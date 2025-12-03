from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user
from datetime import datetime
from models import Usuario

verificar_codigo_bp = Blueprint('verificar_codigo', __name__)


@verificar_codigo_bp.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    pending = session.get('2fa_pending')
    if not pending:
        flash('No hay un proceso de verificación activo. Inicia sesión primero.', 'error')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        if not codigo:
            flash('Ingresa el código enviado a tu correo.', 'error')
            return render_template('verificar_codigo.html')

        # Verificar expiración
        try:
            expires_ts = float(pending.get('expires', 0))
        except Exception:
            expires_ts = 0

        if datetime.utcnow().timestamp() > expires_ts:
            session.pop('2fa_pending', None)
            flash('El código ha expirado. Por favor vuelve a iniciar sesión.', 'error')
            return redirect(url_for('login.login'))

        if codigo == pending.get('code'):
            # Crear objeto usuario y loguear
            usuario_obj = Usuario(pending.get('user_id'), pending.get('nombre'), pending.get('tipo'))
            login_user(usuario_obj)
            session['usuario_id'] = pending.get('user_id')
            session['tipo_usuario'] = pending.get('tipo')
            session.pop('2fa_pending', None)

            flash(f"Bienvenido, {usuario_obj.nombre}!", 'success')
            tipo = usuario_obj.tipo
            if tipo == 'admin':
                return redirect(url_for('admin_dashboard.admin_dashboard'))
            elif tipo == 'Cliente':
                return redirect(url_for('menu_clientes.menu_principal'))
            elif tipo == 'Proveedor':
                return redirect(url_for('menu_provedor.menu'))
            else:
                return redirect(url_for('inicio.index'))
        else:
            flash('Código incorrecto. Revisa tu correo e intenta nuevamente.', 'error')
            return render_template('verificar_codigo.html')

    return render_template('verificar_codigo.html')
