from flask import Blueprint, render_template, flash, session, redirect, url_for, request, current_app
from flask_login import login_required
from bd import conectar_bd
from utils import allowed_file
from werkzeug.utils import secure_filename
import bcrypt
import os

configuracion_bp = Blueprint('configuracion', __name__)

@configuracion_bp.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT tipo FROM usuarios WHERE id = %s", (usuario_id,))
        tipo_usuario = cursor.fetchone()[0]

        if request.method == 'GET':
            cursor.execute("""
                SELECT u.id, u.nombre, u.correo, p.foto, p.biografia
                FROM usuarios u
                LEFT JOIN perfiles p ON u.id = p.usuario_id
                WHERE u.id = %s
            """, (usuario_id,))
            usuario_data = cursor.fetchone()

            usuario = {
                'id': usuario_data[0],
                'nombre': usuario_data[1],
                'correo': usuario_data[2],
                'foto': usuario_data[3] if usuario_data[3] else 'imagenes/default-profile.jpg',
                'biografia': usuario_data[4] if usuario_data[4] else ''
            }

            cursor.close()
            conexion.close()

            if tipo_usuario == "Cliente":
                return render_template('configuracion_clientes.html', usuario=usuario)
            elif tipo_usuario == "Proveedor":
                return render_template('configuracion.html', usuario=usuario)
            else:
                flash("Tipo de usuario desconocido.", "error")
                return redirect(url_for('inicio.inicio'))

        elif request.method == 'POST':
            seccion = request.form.get('seccion')

            cursor.execute("SELECT 1 FROM perfiles WHERE usuario_id = %s", (usuario_id,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO perfiles (usuario_id, foto, biografia)
                    VALUES (%s, %s, %s)
                """, (usuario_id, 'imagenes/default-profile.jpg', ''))

            if seccion == 'perfil':
                nombre = request.form.get('nombre')
                apellido = request.form.get('apellido', '')
                biografia = request.form.get('biografia', '')
                foto = request.files.get('foto')

                if foto and allowed_file(foto.filename):
                    filename = secure_filename(f"{usuario_id}_{foto.filename}")
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    foto.save(filepath)

                    ruta_foto = f"imagenes/{filename}"
                    cursor.execute("""
                        UPDATE perfiles 
                        SET foto = %s, biografia = %s 
                        WHERE usuario_id = %s
                    """, (ruta_foto, biografia, usuario_id))
                else:
                    cursor.execute("""
                        UPDATE perfiles 
                        SET biografia = %s 
                        WHERE usuario_id = %s
                    """, (biografia, usuario_id))

                cursor.execute("""
                    UPDATE usuarios 
                    SET nombre = %s, apellido = %s 
                    WHERE id = %s
                """, (nombre, apellido, usuario_id))

            elif seccion == 'notificaciones':
                flash("Notificaciones no disponibles aún.", "info")
                # Sección reservada para configuración futura de notificaciones

            elif seccion == 'contrasena':
                actual = request.form.get('actual')
                nueva = request.form.get('nueva')
                confirmar = request.form.get('confirmar')

                cursor.execute("SELECT contraseña FROM usuarios WHERE id = %s", (usuario_id,))
                resultado = cursor.fetchone()

                if not resultado or not resultado[0]:
                    flash("La contraseña actual no está configurada correctamente.", "error")
                else:
                    contrasena_actual_bd = resultado[0]

                    if not bcrypt.checkpw(actual.encode('utf-8'), contrasena_actual_bd.encode('utf-8')):
                        flash("La contraseña actual es incorrecta.", "error")
                    elif nueva != confirmar:
                        flash("Las nuevas contraseñas no coinciden.", "error")
                    else:
                        nueva_hash = bcrypt.hashpw(nueva.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cursor.execute("UPDATE usuarios SET contraseña = %s WHERE id = %s", (nueva_hash, usuario_id))
                        flash("Contraseña actualizada correctamente.", "success")

            elif seccion == 'correo':
                nuevo_correo = request.form.get('nuevo_correo')

                if not nuevo_correo:
                    flash("Debes ingresar un nuevo correo.", "error")
                else:
                    cursor.execute("SELECT id FROM usuarios WHERE correo = %s AND id != %s", (nuevo_correo, usuario_id))
                    if cursor.fetchone():
                        flash("El correo ya está registrado por otro usuario.", "error")
                    else:
                        cursor.execute("UPDATE usuarios SET correo = %s WHERE id = %s", (nuevo_correo, usuario_id))
                        flash("Correo actualizado correctamente.", "success")

            # La configuración de accesibilidad se gestiona en el cliente usando localStorage; no se guarda en la base de datos.

            conexion.commit()
            cursor.close()
            conexion.close()

            return redirect(url_for('configuracion.configuracion'))

    except Exception as e:
        print(f"Error al manejar la configuración: {e}")
        flash("Ocurrió un error al manejar la configuración.", "error")
        return redirect(url_for('configuracion.configuracion'))