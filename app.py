# ToDoList_APIs/app.py

import os
from flask import Flask, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Importamos los Blueprints
from routes.auth_routes import auth_bp, init_auth_routes
from routes.tasks_routes import tasks_bp, init_tasks_routes # Importamos el nuevo Blueprint

# Carga las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuración de MongoDB desde las variables de entorno
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY")

if not MONGO_URI:
    raise ValueError("No se ha configurado la variable de entorno MONGO_URI.")
if not SECRET_KEY:
    raise ValueError("No se ha configurado la variable de entorno SECRET_KEY.")

app.config["SECRET_KEY"] = SECRET_KEY

# Conexión a MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client.todo_list_db # Nombre de tu base de datos

# Colecciones de la base de datos
users_collection = db.users
tasks_collection = db.tasks

# Inicializamos los Blueprints con las referencias a las colecciones y a bcrypt
init_auth_routes(users_collection, bcrypt)
init_tasks_routes(tasks_collection, users_collection) # Pasamos las colecciones de tareas y usuarios

# Registramos los Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(tasks_bp, url_prefix='/api') # Usaremos /api como prefijo para las rutas de tareas

@app.route('/')
def home():
    return "¡API de Lista de Tareas funcionando!"

if __name__ == '__main__':
    app.run(host='0.0.0.0') # debug=True para desarrollo, cambiar a False en producción