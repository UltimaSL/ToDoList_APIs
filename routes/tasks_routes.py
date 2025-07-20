# ToDoList_APIs/routes/tasks_routes.py

from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId # Para convertir strings a ObjectId de MongoDB

# Creamos un Blueprint para las rutas de tareas
tasks_bp = Blueprint('tasks_bp', __name__)

# Necesitamos acceso a la colección de tareas y a usuarios si se requiere validar el ID
# Los inicializaremos a través de una función de inicialización del Blueprint
def init_tasks_routes(tasks_collection_ref, users_collection_ref):
    global tasks_collection, users_collection
    tasks_collection = tasks_collection_ref
    users_collection = users_collection_ref # Por si necesitamos validar el id_usuario

# 3. Endpoint Guardar (para agregar o actualizar tareas)
@tasks_bp.route('/tasks', methods=['POST'])
def save_task():
    data = request.get_json()
    id_usuario = data.get('id_usuario') # El ID del usuario al que pertenece la tarea
    notas_usuario = data.get('notas_usuario')
    etiqueta = data.get('etiqueta', '') # Etiqueta es opcional, por defecto vacía
    id_tarea = data.get('id_tarea') # Si se proporciona, es una actualización

    if not all([id_usuario, notas_usuario]):
        return jsonify({"message": "Faltan campos obligatorios (id_usuario, notas_usuario)"}), 400

    # Opcional: Verificar si el id_usuario existe
    # if not users_collection.find_one({"_id": ObjectId(id_usuario)}):
    #     return jsonify({"message": "Usuario no encontrado"}), 404

    # Crear el documento de la tarea
    task_document = {
        "id_usuario": ObjectId(id_usuario), # Asegúrate de que el ID del usuario sea un ObjectId
        "notas_usuario": notas_usuario,
        "etiqueta": etiqueta
    }

    if id_tarea: # Si se proporciona id_tarea, es una actualización
        try:
            # Convertir id_tarea a ObjectId para buscar en MongoDB
            task_object_id = ObjectId(id_tarea)
            # Actualizar la tarea existente
            result = tasks_collection.update_one(
                {"_id": task_object_id, "id_usuario": ObjectId(id_usuario)}, # Asegurar que el usuario sea dueño de la tarea
                {"$set": task_document}
            )
            if result.matched_count == 0:
                return jsonify({"message": "Tarea no encontrada o no pertenece al usuario"}), 404
            return jsonify({"message": "Tarea actualizada exitosamente", "id_tarea": id_tarea}), 200
        except Exception:
            return jsonify({"message": "ID de tarea inválido"}), 400
    else: # Si no se proporciona id_tarea, es una nueva tarea
        # Insertar la nueva tarea
        result = tasks_collection.insert_one(task_document)
        return jsonify({"message": "Tarea guardada exitosamente", "id_tarea": str(result.inserted_id)}), 201

# 4. Endpoint Borrado
@tasks_bp.route('/tasks/<string:id_tarea>', methods=['DELETE'])
def delete_task(id_tarea):
    # En una aplicación real, también verificarías el id_usuario para asegurar que el usuario
    # solo pueda borrar sus propias tareas. Por ahora, solo borraremos por id_tarea.
    try:
        task_object_id = ObjectId(id_tarea)
        result = tasks_collection.delete_one({"_id": task_object_id})

        if result.deleted_count == 0:
            return jsonify({"message": "Tarea no encontrada"}), 404
        
        return jsonify({"message": "Tarea eliminada exitosamente"}), 200
    except Exception:
        return jsonify({"message": "ID de tarea inválido"}), 400