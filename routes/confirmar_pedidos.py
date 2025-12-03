from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd
from correo_utils import enviar_correo_pedido

confirmar_pedidos_bp = Blueprint('confirmar_pedidos', __name__)

@confirmar_pedidos_bp.route('/proceso_pedido')
@login_required
def proceso_pedido():
    """Página con formularios - redirige aquí desde confirmar_pedido"""
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para confirmar tu pedido.", "error")
        return redirect(url_for('login.login'))
    
    cliente_id = session.get('usuario_id')
    carrito = session.get('carrito', [])
    
    if not carrito:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for('carrito.carrito'))
    
    # Calcular total y productos para mostrar en el formulario
    total = 0
    productos = []
    
    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            
            for item in carrito:
                cursor.execute("""
                    SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria,
                           ip.ruta_imagen
                    FROM productos p
                    JOIN categorias c ON p.categoria_id = c.id
                    LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                    WHERE p.id = %s
                """, (item['producto_id'],))
                producto = cursor.fetchone()
                if producto:
                    subtotal = producto[3] * item['cantidad']
                    total += subtotal
                    productos.append({
                        'id': producto[0],
                        'nombre': producto[1],
                        'descripcion': producto[2],
                        'precio': producto[3],
                        'categoria': producto[4],
                        'imagen': producto[5],
                        'cantidad': item['cantidad'],
                        'subtotal': subtotal
                    })
            
            cursor.close()
            conexion.close()
            
    except Exception as e:
        print("Error al cargar productos del carrito:", e)
        flash("Error al cargar el carrito", "error")
        return redirect(url_for('carrito.carrito'))
    
    return render_template('confirmacion_pedidos.html', 
                         productos=productos, 
                         total=total, 
                         usuario_id=cliente_id,
                         modo='formulario')

@confirmar_pedidos_bp.route('/confirmar_pedidos', methods=['POST'])
@login_required
def confirmar_pedido():
    """Esta ruta ahora solo redirige a proceso_pedido"""
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para confirmar tu pedido.", "error")
        return redirect(url_for('login.login'))

    # En lugar de procesar inmediatamente, redirigir a la página de formularios
    return redirect(url_for('confirmar_pedidos.proceso_pedido'))

@confirmar_pedidos_bp.route('/finalizar_pedido', methods=['POST'])
@login_required
def finalizar_pedido():
    """Nueva ruta para procesar el pedido final desde los formularios"""
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para confirmar tu pedido.", "error")
        return redirect(url_for('login.login'))

    # Recibir datos del formulario
    empaque = request.form.get('package', 'costal')
    metodo_entrega = request.form.get('delivery-method', 'domicilio')
    metodo_pago = request.form.get('payment-method', 'transferencia')
    factura = request.form.get('invoice', 'no')
    confirmacion = request.form.get('confirmation', 'notificacion')
    comentarios = request.form.get('comentarios', '')
    telefono = request.form.get('telefono', '')
    email = request.form.get('email', '')
    
    # Datos de facturación si es necesario
    datos_fiscales = None
    if factura == 'si':
        datos_fiscales = {
            'rfc': request.form.get('rfc', ''),
            'razon_social': request.form.get('razon_social', ''),
            'direccion_fiscal': request.form.get('direccion_fiscal', '')
        }

    cliente_id = session.get('usuario_id')
    carrito = session.get('carrito', [])

    if not carrito:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for('carrito.carrito'))

    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('carrito.carrito'))

        cursor = conexion.cursor()

        # Obtener correo del cliente
        cursor.execute("SELECT correo FROM usuarios WHERE id = %s", (cliente_id,))
        resultado = cursor.fetchone()
        if not resultado:
            flash("Error: No se encontró el usuario en la base de datos.", "error")
            return redirect(url_for('carrito.carrito'))
        correo_cliente = resultado[0]

        # Calcular total y preparar productos
        total = 0
        productos_pedido = []
        detalles_pedido = []
        
        for item in carrito:
            producto_id = item.get('producto_id')
            cantidad = item.get('cantidad', 1)

            if not producto_id:
                flash("Error: Falta el producto en el carrito.", "error")
                return redirect(url_for('carrito.carrito'))

            cursor.execute("""
                SELECT nombre, precio, proveedor_id, descripcion 
                FROM productos WHERE id = %s
            """, (producto_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                nombre_producto = resultado[0]
                precio = resultado[1]
                proveedor_id = resultado[2]
                descripcion = resultado[3]
                
                subtotal = precio * cantidad
                total += subtotal
                
                productos_pedido.append({
                    'nombre': nombre_producto,
                    'cantidad': cantidad,
                    'precio': precio,
                    'subtotal': subtotal,
                    'descripcion': descripcion
                })
                
                detalles_pedido.append({
                    'producto_id': producto_id,
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'proveedor_id': proveedor_id
                })
            else:
                flash(f"Error: Producto con ID {producto_id} no encontrado.", "error")
                return redirect(url_for('carrito.carrito'))

        # Insertar pedido principal
        cursor.execute("""
            INSERT INTO pedidos (cliente_id, total, estado, metodo_entrega, metodo_pago, 
                               tipo_empaque, requiere_factura, comentarios, telefono_contacto)
            VALUES (%s, %s, 'pendiente', %s, %s, %s, %s, %s, %s) RETURNING id
        """, (cliente_id, total, metodo_entrega, metodo_pago, empaque, factura, comentarios, telefono))
        
        pedido_id = cursor.fetchone()[0]

        # Insertar detalles del pedido
        for detalle in detalles_pedido:
            cursor.execute("""
                INSERT INTO detalles_pedidos (pedido_id, producto_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, detalle['producto_id'], detalle['cantidad'], detalle['precio_unitario']))

            # Crear notificación para el proveedor
            mensaje_notificacion = f"Nuevo pedido #{pedido_id}: {detalle['cantidad']} unidades"
            cursor.execute("""
                INSERT INTO notificaciones (proveedor_id, cliente_id, producto_id, mensaje, estado, fecha)
                VALUES (%s, %s, %s, %s, 'Pendiente', NOW())
            """, (detalle['proveedor_id'], cliente_id, detalle['producto_id'], mensaje_notificacion))

        # Insertar datos fiscales si es necesario
        if factura == 'si' and datos_fiscales:
            cursor.execute("""
                INSERT INTO datos_facturacion (pedido_id, rfc, razon_social, direccion_fiscal)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, datos_fiscales['rfc'], datos_fiscales['razon_social'], datos_fiscales['direccion_fiscal']))

        conexion.commit()
        cursor.close()
        conexion.close()

        # Enviar correo de confirmación
        try:
            enviar_correo_pedido(correo_cliente, pedido_id, total, productos_pedido)
        except Exception as e:
            print("Error al enviar correo:", e)
            # No romper el flujo si falla el correo

        # Limpiar carrito
        session.pop('carrito', None)

        flash("Pedido confirmado correctamente. Se ha enviado un correo de confirmación.", "success")

        return render_template('confirmacion_pedidos.html', 
                             pedido_id=pedido_id, 
                             total=total, 
                             productos_pedido=productos_pedido,
                             metodo_entrega=metodo_entrega,
                             metodo_pago=metodo_pago,
                             modo='confirmacion')

    except Exception as e:
        print("Error al confirmar el pedido:", e)
        flash("Ocurrió un error al confirmar el pedido. Intenta nuevamente.", "error")
        return redirect(url_for('carrito.carrito'))