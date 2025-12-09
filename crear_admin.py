import bcrypt
from bd import conectar_bd

def admin_existe(correo):
    """Verifica si un admin con ese correo ya existe."""
    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE correo = %s AND tipo = 'admin'", (correo,))
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()
            return resultado is not None
        return False
    except Exception as e:
        print(f"Error al verificar admin: {e}")
        return False

def crear_admin(nombre, correo, contraseña_plana, fecha_nacimiento):
    try:
        # Verificar si el admin ya existe
        if admin_existe(correo):
            print(f"Administrador con correo '{correo}' ya existe. Saltando creación.")
            return True
        
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()


            salt = bcrypt.gensalt()
            contraseña_hash = bcrypt.hashpw(contraseña_plana.encode('utf-8'), salt).decode('utf-8')


            cursor.execute("""
                INSERT INTO usuarios (nombre, correo, contraseña, tipo, fecha_nacimiento)
                VALUES (%s, %s, %s, 'admin', %s)
            """, (nombre, correo, contraseña_hash, fecha_nacimiento))

            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"Administrador '{nombre}' creado exitosamente.")
            return True
        else:
            print("Error: No se pudo conectar a la base de datos.")
            return False
    except Exception as e:
        print("Error al crear administrador:", e)
        return False

if __name__ == "__main__":
    crear_admin('Admin Charly', 'edgar@gmail.com', 'admin123', '2004-04-04')