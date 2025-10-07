from flask import Blueprint, session, redirect, url_for, flash, request, render_template, jsonify
from flask_login import login_required
from bd import conectar_bd
import mercadopago
import os
import json

mercadopago_bp = Blueprint('mercadopago', __name__)

# Función para guardar el pedido en la base de datos
def guardar_pedido_en_bd(cliente_id, total, preference_id):
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO pedidos (cliente_id, total, estado, preference_id, fecha)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        """, (cliente_id, total, 'Pendiente', preference_id))
        pedido_id = cursor.fetchone()[0]
        conexion.commit()
        cursor.close()
        conexion.close()
        return pedido_id
    except Exception as e:
        print(f"❌ Error al guardar el pedido: {e}")
        return None

@mercadopago_bp.route('/mercadopago', methods=['POST'])
@login_required
def mercadopago_pago():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para pagar.", "error")
        return redirect(url_for('login.login'))

    carrito_json = request.form.get('carrito_json')
    if carrito_json:
        try:
            session['carrito'] = json.loads(carrito_json)
        except Exception as e:
            print("❌ Error al cargar carrito_json:", e)
            session['carrito'] = []

    cliente_id = session.get('usuario_id')
    carrito = session.get('carrito', [])

    if not carrito:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for('carrito.carrito'))

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("SELECT correo FROM usuarios WHERE id = %s", (cliente_id,))
        resultado = cursor.fetchone()
        if not resultado:
            flash("No se encontró el usuario en la base de datos.", "error")
            return redirect(url_for('carrito.carrito'))
        correo_cliente = resultado[0]
        cursor.close()
        conexion.close()

        access_token =  "APP_USR-6772237074984826-092723-fbc0fb9068aa124823dacf9d83ea57e6-1276496548"
        sdk = mercadopago.SDK(access_token)

        items_mercado_pago = []
        total = 0
        productos_pedido = []

        conexion = conectar_bd()
        cursor = conexion.cursor()
        for item in carrito:
            producto_id = item.get('producto_id')
            cursor.execute("SELECT nombre, precio, proveedor_id FROM productos WHERE id = %s", (producto_id,))
            resultado = cursor.fetchone()
            if resultado:
                nombre_producto, precio, proveedor_id = resultado
                cantidad = item['cantidad']
                subtotal = precio * cantidad
                total += subtotal
                productos_pedido.append((nombre_producto, cantidad, proveedor_id, producto_id, precio))
                items_mercado_pago.append({
                    "title": nombre_producto[:127],
                    "quantity": int(cantidad),
                    "currency_id": "MXN",
                    "unit_price": float(precio)
                })
            else:
                flash(f"Producto con ID {producto_id} no encontrado.", "error")
                return redirect(url_for('carrito.carrito'))
        cursor.close()
        conexion.close()

        base_url = "https://threadless-cameron-historically.ngrok-free.dev"

        preference_data = {
    "items": items_mercado_pago,
    "back_urls": {
        "success": f"{base_url}/pago_exitoso",
        "failure": f"{base_url}/pago_fallido",
        "pending": f"{base_url}/pago_pendiente"
    },
    "auto_return": "approved",
    "metadata": {
        "cliente_id": cliente_id,
        "correo_cliente": correo_cliente
    },
    "statement_descriptor": "AGRIMAX",
    "payment_methods": {
        "excluded_payment_types": [],          # No excluye nada
        "installments": 12,                    # Hasta 12 meses
       
    }
}

        preference_response = sdk.preference().create(preference_data)

        if not preference_response or "response" not in preference_response or "init_point" not in preference_response["response"]:
            print("❌ Respuesta inválida de Mercado Pago:", preference_response)
            flash("Error al crear la preferencia de pago.", "error")
            return redirect(url_for('carrito.carrito'))

        init_point = preference_response["response"]["init_point"]
        preference_id = preference_response["response"]["id"]

        pedido_id = guardar_pedido_en_bd(cliente_id, total, preference_id)
        if not pedido_id:
            flash("No se pudo registrar el pedido", "error")
            return redirect(url_for('carrito.carrito'))

        session['pedido_pendiente'] = {
            'cliente_id': cliente_id,
            'total': total,
            'productos_pedido': productos_pedido,
            'preference_id': preference_id,
            'pedido_id': pedido_id
        }

        print("✅ Redirigiendo a Mercado Pago:", init_point)
        return redirect(init_point)

    except Exception as e:
        print("❌ Error al procesar el pago con Mercado Pago:", e)
        flash("Ocurrió un error al procesar el pago. Intenta nuevamente.", "error")
        return redirect(url_for('carrito.carrito'))

@mercadopago_bp.route('/pago_exitoso')
def pago_exitoso():
    pedido = session.get('pedido_pendiente')
    if pedido:
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("UPDATE pedidos SET estado = 'Aprobado' WHERE id = %s", (pedido['pedido_id'],))
            conexion.commit()
            cursor.close()
            conexion.close()
        except Exception as e:
            print(f"❌ Error al actualizar estado del pedido: {e}")

        print("🧾 Pedido confirmado:", pedido)
        flash("¡Pago exitoso! Gracias por tu compra.", "success")
        session.pop('carrito', None)
        session.pop('pedido_pendiente', None)
    else:
        flash("No se encontró información del pedido.", "warning")
    return redirect(url_for('inicio.inicio'))

@mercadopago_bp.route('/pago_fallido')
def pago_fallido():
    flash("El pago fue rechazado. Intenta con otra tarjeta.", "error")
    session.pop('pedido_pendiente', None)
    return redirect(url_for('carrito.carrito'))

@mercadopago_bp.route('/pago_pendiente')
def pago_pendiente():
    flash("Tu pago está pendiente. Te notificaremos cuando se confirme.", "info")
    return redirect(url_for('carrito.carrito'))