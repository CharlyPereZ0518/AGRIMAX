from flask import session

from bd import conectar_bd


def inject_usuario_con_cache():
    """
    Versión optimizada con caché en sesión.
    Evita consultas repetidas a la base de datos.
    Usa esta versión si tienes muchos usuarios simultáneos.
    """
    usuario_default = {
        'nivel_contraste': 'normal',
        'cursor_size': 'default',
        'modo_lector': 'off'
    }

    if 'usuario_id' not in session:
        return {'usuario': usuario_default}

    # Verificar si ya está en caché
    if 'usuario_cache' in session:
        return {'usuario': session['usuario_cache']}

    # Si no está en caché, consultar BD
    try:
        usuario_id = session['usuario_id']
        conexion = conectar_bd()

        if not conexion:
            return {'usuario': usuario_default}

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT 
                u.id, 
                u.nombre, 
                u.correo, 
                u.tipo,
                COALESCE(p.foto, 'imagenes/default-profile.jpg') as foto,
                COALESCE(p.cursor_size, 'default') as cursor_size,
                COALESCE(p.modo_lector, 'off') as modo_lector,
                COALESCE(p.nivel_contraste, 'normal') as nivel_contraste,
                p.usuario_id
            FROM usuarios u
            LEFT JOIN perfiles p ON u.id = p.usuario_id
            WHERE u.id = %s
        """, (usuario_id,))

        usuario_data = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario_data:
            usuario = {
                'id': usuario_data[0],
                'nombre': usuario_data[1],
                'correo': usuario_data[2],
                'tipo': usuario_data[3],
                'foto': usuario_data[4],
                'cursor_size': usuario_data[5],
                'modo_lector': usuario_data[6],
                'nivel_contraste': usuario_data[7],
                'usuario_id': usuario_data[8]
            }

            # Guardar en caché de sesión
            session['usuario_cache'] = usuario
            session.modified = True

            return {'usuario': usuario}

    except Exception as e:
        print(f"Error en context_processor inject_usuario_con_cache: {e}")

    return {'usuario': usuario_default}
def limpiar_cache_usuario():
    """
    Función auxiliar para limpiar el caché del usuario.
    Llamar esta función después de actualizar preferencias del usuario.
    """
    if 'usuario_cache' in session:
        del session['usuario_cache']
        session.modified = True