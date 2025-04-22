from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql, bcrypt
import re

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para iniciar sesión"""
    if request.method == 'POST':
        # Obtener datos del formulario
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        
        # Validar datos
        if not correo or not contrasena:
            flash('Por favor, completa todos los campos', 'warning')
            return render_template('auth/login.html')
        
        # Consultar el usuario
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nombre, correo, contrasena, rol FROM usuarios WHERE correo = %s", [correo])
        usuario = cur.fetchone()
        cur.close()
        
        # Verificar si el usuario existe y la contraseña es correcta
        if usuario and bcrypt.check_password_hash(usuario['contrasena'], contrasena):
            # Guardar datos en la sesión
            session['usuario_id'] = usuario['id']
            session['nombre'] = usuario['nombre']
            session['correo'] = usuario['correo']
            session['rol'] = usuario['rol']
            
            # Redireccionar según el rol
            if usuario['rol'] == 'cliente':
                return redirect(url_for('cliente.dashboard'))
            elif usuario['rol'] == 'agente':
                return redirect(url_for('agente.dashboard'))
            elif usuario['rol'] == 'proveedor':
                return redirect(url_for('proveedor.dashboard'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Ruta para registrar un nuevo usuario"""
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        confirmar_contrasena = request.form['confirmar_contrasena']
        rol = request.form['rol'] if 'rol' in request.form else 'cliente'
        
        # Validaciones básicas
        if not nombre or not correo or not contrasena or not confirmar_contrasena:
            flash('Por favor, completa todos los campos', 'warning')
            return render_template('auth/register.html')
        
        if contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden', 'warning')
            return render_template('auth/register.html')
        
        # Validar formato de correo
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            flash('Por favor, ingresa un correo electrónico válido', 'warning')
            return render_template('auth/register.html')
        
        # Verificar si el correo ya está registrado
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM usuarios WHERE correo = %s", [correo])
        usuario_existente = cur.fetchone()
        
        if usuario_existente:
            flash('El correo ya está registrado', 'warning')
            cur.close()
            return render_template('auth/register.html')
        
        # Encriptar contraseña
        hashed_password = bcrypt.generate_password_hash(contrasena).decode('utf-8')
        
        # Insertar usuario en la base de datos
        try:
            cur.execute(
                "INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES (%s, %s, %s, %s)",
                (nombre, correo, hashed_password, rol)
            )
            mysql.connection.commit()
            cur.close()
            
            flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error al registrar: {str(e)}', 'danger')
            cur.close()
    
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    """Cerrar sesión"""
    # Eliminar datos de la sesión
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('auth.login'))