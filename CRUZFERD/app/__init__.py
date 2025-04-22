from flask import Flask
from flask_mysqldb import MySQL
import os
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Configuración
app.config.from_pyfile('config.py')
app.secret_key = 'clave_secreta_para_sesiones'

# Instancia MySQL
mysql = MySQL(app)

# Instancia Bcrypt
bcrypt = Bcrypt(app)

# Importar rutas
from app.routes import auth, cliente, agente, proveedor, public

# Registrar Blueprints
app.register_blueprint(public.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(cliente.bp)
app.register_blueprint(agente.bp)
app.register_blueprint(proveedor.bp)