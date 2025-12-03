from flask import Blueprint, render_template, request, session, jsonify

chat_bp = Blueprint('chat', __name__)

# respuestas compartidas
common_kb = {
    "que es agrimax": "Agrimax es una plataforma que conecta productores agrícolas con clientes para comprar frutas, verduras y hortalizas.",
    "productos venden": "Ofrecemos frutas, verduras, legumbres y hortalizas frescas, directamente del campo.",
    "registrarme": "Haz clic en 'Registrarse' en la página principal, completa tus datos y confirma tu correo electrónico.",
    "iniciar sesion": "Haz clic en 'Iniciar sesión' en la página principal e ingresa tu correo y contraseña.",
}

# KB específica por rol
kb_cliente = {
    **common_kb,
    "ver carrito": "Haz clic en el ícono del carrito 🛒 en la parte superior derecha del sitio.",
    "agregar productos": "Entra a cualquier categoría, selecciona un producto y haz clic en 'Agregar al carrito'.",
    "finalizar compra": "Revisa los productos en el carrito y haz clic en 'Realizar compra' para confirmar tu pedido.",
}

kb_proveedor = {
    **common_kb,
    "vender productos": "Los productores pueden registrarse, completar su perfil y subir productos desde su panel.",
    "subir producto": "En el panel de proveedor ve a 'Mis Productos' > 'Agregar producto' y completa los campos requeridos.",
    "ver pedidos": "Desde el panel de proveedor puedes ver los pedidos recibidos y su estado.",
}

kb_guest = {
    **common_kb,
    "info publica": "Puedes navegar las categorías y ver productos sin iniciar sesión, pero para comprar debes registrarte.",
}

# mapa de keywords (puede compartirse)
keyword_map = {
    "carrito": "ver carrito", "agregar": "agregar productos", "finalizar": "finalizar compra",
    "vender": "vender productos", "subir": "subir producto", "pedidos": "ver pedidos",
    "registr": "registrarme", "producto": "productos venden", "que es": "que es agrimax"
}

def get_role_from_request():
    # prioridad: query param -> session -> guest
    role = (request.args.get('role') or session.get('role') or 'guest').lower()
    if role not in ('cliente', 'proveedor', 'guest'):
        role = 'guest'
    return role

def get_kb_for_role(role):
    if role == 'proveedor':
        return kb_proveedor
    if role == 'cliente':
        return kb_cliente
    return kb_guest

def simple_fallback_match(text, kb):
    words = [w for w in text.split() if len(w) > 2]
    best = None
    best_score = 0
    for key, answer in kb.items():
        score = 0
        for w in words:
            if w in key: score += 2
            if w in answer.lower(): score += 1
        if score > best_score:
            best_score = score
            best = key
    return best if best_score >= 1 else None

@chat_bp.route('/chat')
def chat_page():
    # renderiza la plantilla (chat.html). La plantilla puede seguir siendo neutra (JS cliente).
    # opcional: pasar role al template para UI (ej: cambiar título)
    role = get_role_from_request()
    return render_template('chat.html', chat_role=role)

@chat_bp.route('/api/chat/ask', methods=['POST'])
def api_chat_ask():
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip().lower()
    if not text:
        return jsonify({"error": "Texto vacío"}), 400

    role = get_role_from_request()
    kb = get_kb_for_role(role)

    # historial opcional
    history = session.get('chat_history', [])
    history.append({"role": "user", "text": text, "role_type": role})
    session['chat_history'] = history

    # búsqueda exacta
    if text in kb:
        answer = kb[text]
        history.append({"role": "bot", "text": answer})
        session['chat_history'] = history
        return jsonify({"matched": True, "answer": answer, "role": role})

    # keyword map
    for k, mapped in keyword_map.items():
        if k in text:
            answer = kb.get(mapped)
            if answer:
                history.append({"role": "bot", "text": answer})
                session['chat_history'] = history
                return jsonify({"matched": True, "answer": answer, "role": role})

    # fallback
    best = simple_fallback_match(text, kb)
    if best:
        answer = kb[best]
        history.append({"role": "bot", "text": answer})
        session['chat_history'] = history
        return jsonify({"matched": True, "answer": answer, "role": role})

    suggestions = list(kb.keys())[:6]
    reply = "No encontré una respuesta exacta. Prueba con: " + ", ".join(suggestions)
    history.append({"role": "bot", "text": reply})
    session['chat_history'] = history
    return jsonify({"matched": False, "answer": reply, "suggestions": suggestions, "role": role})

@chat_bp.route('/api/chat/state', methods=['GET'])
def api_chat_state():
    return jsonify({"history": session.get('chat_history', []), "role": get_role_from_request()})