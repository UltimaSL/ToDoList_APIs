# ToDoList_APIs/routes/auth_routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId

# Creamos un Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth_bp', __name__)

# Necesitamos acceso a bcrypt y a las colecciones de la base de datos
# Los inicializaremos dentro de la función register_auth_routes
# O podemos hacerlos accesibles de otra forma, como usando current_app.config

# Función para inicializar el Blueprint con las dependencias de DB y Bcrypt
def init_auth_routes(users_collection_ref, bcrypt_ref):
    global users_collection, bcrypt
    users_collection = users_collection_ref
    bcrypt = bcrypt_ref

# 1. Endpoint Registrar
@auth_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    correo_usuario = data.get('correo_usuario')
    contrasena_usuario = data.get('contrasena_usuario')

    if not all([nombre_usuario, correo_usuario, contrasena_usuario]):
        return jsonify({"message": "Faltan campos obligatorios"}), 400

    # Verificar si el correo ya existe
    if users_collection.find_one({"correo_usuario": correo_usuario}):
        return jsonify({"message": "El correo electrónico ya está registrado"}), 409

    # Hashear la contraseña antes de guardarla
    hashed_password = bcrypt.generate_password_hash(contrasena_usuario).decode('utf-8')

    # Guardar el nuevo usuario en la base de datos
    user_id = users_collection.insert_one({
        "nombre_usuario": nombre_usuario,
        "correo_usuario": correo_usuario,
        "contrasena_usuario": hashed_password # Almacenar la contraseña hasheada
    }).inserted_id

    return jsonify({"message": "Usuario registrado exitosamente", "user_id": str(user_id)}), 201

# 2. Endpoint LogIn
@auth_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    correo_usuario = data.get('correo_usuario')
    contrasena_usuario = data.get('contrasena_usuario')

    if not all([correo_usuario, contrasena_usuario]):
        return jsonify({"message": "Faltan campos obligatorios"}), 400

    # Buscar al usuario por correo electrónico
    user = users_collection.find_one({"correo_usuario": correo_usuario})

    if user:
        # Verificar la contraseña hasheada
        if bcrypt.check_password_hash(user['contrasena_usuario'], contrasena_usuario):
            # En una aplicación real, aquí se generaría un JWT o una sesión.
            # Por ahora, solo devolveremos un mensaje de éxito y el ID del usuario.
            return jsonify({"message": "Inicio de sesión exitoso", "user_id": str(user['_id'])}), 200
        else:
            return jsonify({"message": "Correo o contraseña incorrectos"}), 401
    else:
        return jsonify({"message": "Correo o contraseña incorrectos"}), 401