from flask import Blueprint, render_template, flash, session, redirect, url_for, request, jsonify
from flask_login import login_required
from bd import conectar_bd

notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/api/notificaciones/count')
@login_required
def count_notificaciones():
    """API endpoint para obtener el conteo de notificaciones no leídas"""
    proveedor_id = session.get('usuario_id')
    
    try:
        conexion = conectar_bd()
        if not conexion:
            return jsonify({'count': 0})

        cursor = conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM notificaciones 
            WHERE proveedor_id = %s AND leido = FALSE
        """, (proveedor_id,))
        
        count = cursor.fetchone()[0]
        cursor.close()
        conexion.close()
        
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error al contar notificaciones: {e}")
        return jsonify({'count': 0})

@notificaciones_bp.route('/api/notificaciones/list')
@login_required
def list_notificaciones():
    """API endpoint para obtener lista de notificaciones recientes"""
    proveedor_id = session.get('usuario_id')
    
    try:
        conexion = conectar_bd()
        if not conexion:
            return jsonify({'notificaciones': []})

        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, mensaje, leido, fecha
            FROM notificaciones 
            WHERE proveedor_id = %s 
            ORDER BY fecha DESC 
            LIMIT 10
        """, (proveedor_id,))
        
        notificaciones = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        # Formatear datos
        notificaciones_list = []
        for notif in notificaciones:
            notificaciones_list.append({
                'id': notif[0],
                'mensaje': notif[1],
                'leido': notif[2],
                'fecha': notif[3].isoformat() if notif[3] else None
            })
        
        return jsonify({'notificaciones': notificaciones_list})
    except Exception as e:
        print(f"Error al listar notificaciones: {e}")
        return jsonify({'notificaciones': []})

@notificaciones_bp.route('/notificaciones')
@login_required
def notificaciones():
    if session.get('tipo_usuario') != "Proveedor":
        flash("Solo los proveedores pueden acceder a las notificaciones.", "error")
        return redirect(url_for('menu_provedor.menu'))

    proveedor_id = session.get('usuario_id')
    print("Proveedor ID en sesión:", proveedor_id)

    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('menu_provedor.menu'))

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT n.id, n.mensaje, n.leido, n.fecha, p.nombre AS producto, 
                   COALESCE(ip.ruta_imagen, 'static/imagenes/default-product.jpg') AS imagen, 
                   n.estado, u.nombre AS cliente
            FROM notificaciones n
            JOIN productos p ON n.producto_id = p.id
            LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
            JOIN usuarios u ON n.cliente_id = u.id
            WHERE n.proveedor_id = %s
            ORDER BY n.fecha DESC;
        """, (proveedor_id,))

        notificaciones = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        notificaciones_lista = []
        for fila in notificaciones:
            if len(fila) == len(columnas):
                notificaciones_lista.append(dict(zip(columnas, fila)))
            else:
                print(f"Error: Tamaño de fila {len(fila)} no coincide con columnas {len(columnas)}")

        print("DEBUG: Notificaciones procesadas correctamente:", notificaciones_lista)

        cursor.close()
        conexion.close()

        if not notificaciones_lista:
            flash("No tienes notificaciones en este momento.", "info")
            return redirect(url_for('menu_provedor.menu'))

        return render_template('notificaciones.html', notificaciones=notificaciones_lista)

    except Exception as e:
        print("Error al cargar las notificaciones:", e)
        flash("Error al cargar las notificaciones. Por favor, inténtalo de nuevo.", "error")
        return redirect(url_for('menu_provedor.menu'))

@notificaciones_bp.route('/marcar_leido/<int:notificacion_id>', methods=['POST'])
@login_required
def marcar_leido(notificacion_id):
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        
        cursor.execute("""
            UPDATE notificaciones 
            SET leido = TRUE 
            WHERE id = %s AND proveedor_id = %s
        """, (notificacion_id, session.get('usuario_id')))
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        flash("Notificación marcada como leída.", "success")
        
    except Exception as e:
        print("Error al marcar notificación como leída:", e)
        flash("Error al marcar la notificación como leída.", "error")
    
    return redirect(url_for('notificaciones.notificaciones'))