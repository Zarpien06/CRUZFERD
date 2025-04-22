from functools import wraps
from flask import session, redirect, url_for, flash

def rol_required(rol):
    """
    Decorador para proteger rutas según el rol del usuario
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si el usuario está logueado
            if 'usuario_id' not in session:
                flash('Debes iniciar sesión para acceder a esta página', 'danger')
                return redirect(url_for('auth.login'))
            
            # Verificar si el usuario tiene el rol requerido
            if session.get('rol') != rol:
                flash('No tienes permiso para acceder a esta página', 'danger')
                return redirect(url_for('auth.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_required(f):
    """
    Decorador para verificar si el usuario ha iniciado sesión
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function