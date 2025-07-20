# ToDoList_APIs/routes/tasks_routes.py

from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

# Creamos un Blueprint para las rutas de tareas
tasks_bp = Blueprint('tasks_bp', __name__)

# Variables globales para las colecciones, se inicializarán desde app.py
tasks_collection = None
users_collection = None

def init_tasks_routes(tasks_collection_ref, users_collection_ref):
    global tasks_collection, users_collection
    tasks_collection = tasks_collection_ref
    users_collection = users_collection_ref

# Endpoint para guardar/actualizar tareas
@tasks_bp.route('/tasks', methods=['POST'])
def save_task():
    data = request.get_json()
    id_usuario = data.get('id_usuario')
    notas_usuario = data.get('notas_usuario')
    etiqueta = data.get('etiqueta', '')
    is_done = data.get('is_done', False) # <-- AÑADIDO: Campo is_done (por defecto False)
    id_tarea = data.get('id_tarea')

    if not all([id_usuario, notas_usuario]):
        return jsonify({"message": "Faltan campos obligatorios (id_usuario, notas_usuario)"}), 400

    task_document = {
        "id_usuario": ObjectId(id_usuario),
        "notas_usuario": notas_usuario,
        "etiqueta": etiqueta,
        "is_done": is_done # <-- AÑADIDO: Guardar el estado is_done
    }

    if id_tarea:
        try:
            task_object_id = ObjectId(id_tarea)
            result = tasks_collection.update_one(
                {"_id": task_object_id, "id_usuario": ObjectId(id_usuario)},
                {"$set": task_document}
            )
            if result.matched_count == 0:
                return jsonify({"message": "Tarea no encontrada o no pertenece al usuario"}), 404
            return jsonify({"message": "Tarea actualizada exitosamente", "id_tarea": id_tarea}), 200
        except Exception:
            return jsonify({"message": "ID de tarea inválido"}), 400
    else:
        result = tasks_collection.insert_one(task_document)
        return jsonify({"message": "Tarea guardada exitosamente", "id_tarea": str(result.inserted_id)}), 201

# Endpoint para obtener todas las tareas para un usuario
@tasks_bp.route('/tasks/user/<string:user_id>', methods=['GET'])
def get_tasks_by_user(user_id):
    try:
        user_object_id = ObjectId(user_id)
        
        tasks_cursor = tasks_collection.find({"id_usuario": user_object_id}).sort([("_id", -1)])
        
        tasks_list = []
        for task in tasks_cursor:
            task['_id'] = str(task['_id'])
            task['id_usuario'] = str(task['id_usuario'])
            # <-- AÑADIDO: Asegurarse de que is_done esté presente para todas las tareas
            # Si una tarea antigua no tiene 'is_done', se le asigna False por defecto al devolverla
            task['is_done'] = task.get('is_done', False) 
            tasks_list.append(task)
        
        if not tasks_list:
            return jsonify({"message": "No hay tareas para este usuario"}), 404
        
        return jsonify(tasks_list), 200
    except Exception as e:
        return jsonify({"message": f"ID de usuario inválido o error en el servidor: {e}"}), 400

# Endpoint Borrado
@tasks_bp.route('/tasks/<string:id_tarea>', methods=['DELETE'])
def delete_task(id_tarea):
    try:
        task_object_id = ObjectId(id_tarea)
        result = tasks_collection.delete_one({"_id": task_object_id})

        if result.deleted_count == 0:
            return jsonify({"message": "Tarea no encontrada"}), 404
        
        return jsonify({"message": "Tarea eliminada exitosamente"}), 200
    except Exception:
        return jsonify({"message": "ID de tarea inválido"}), 400