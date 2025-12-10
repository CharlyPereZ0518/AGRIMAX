from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

menu_provedor_bp = Blueprint('menu_provedor', __name__)

@menu_provedor_bp.route('/menu')
@login_required
def menu():
    usuario_id = session.get('usuario_id') 
    if not usuario_id:
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('login.login'))

    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, 
                       p.fecha_creacion, ip.ruta_imagen
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                WHERE p.proveedor_id = %s
                ORDER BY p.fecha_creacion DESC
            """, (usuario_id,))
            productos = cursor.fetchall()

            cursor.close()
            conexion.close()

            productos_procesados = []
            for producto in productos:
                # Debug: mostrar ruta original
                ruta_imagen = producto[6]
                print(f"🖼️ DEBUG - Producto: {producto[1]}, Ruta BD: '{ruta_imagen}'")
                
                # Generar URL de imagen
                if ruta_imagen:
                    imagen_url = f"/static/{ruta_imagen}"
                else:
                    imagen_url = '/static/imagenes/default-product.jpg'
                
                print(f"✅ DEBUG - URL final: '{imagen_url}'")
                
                productos_procesados.append({
                    'id': producto[0],
                    'nombre': producto[1],
                    'descripcion': producto[2],
                    'precio': producto[3],
                    'categoria': producto[4],
                    'fecha_creacion': producto[5],
                    'imagen': imagen_url
                })

            return render_template('menu_provedor.html', usuario_id=usuario_id, productos=productos_procesados)
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('login.login'))
    except Exception as e:
        print("Error al cargar los productos del proveedor:", e)
        flash("Ocurrió un error al cargar los productos. Intenta nuevamente.", "error")
        return redirect(url_for('login.login'))