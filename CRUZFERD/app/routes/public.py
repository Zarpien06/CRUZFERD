from flask import Blueprint, render_template, redirect, url_for
from app import mysql 

# Crear el blueprint para las rutas públicas
bp = Blueprint('public', __name__)

@bp.route('/')
def index():
    """Página principal de la aplicación turística"""
    # Obtener algunas ofertas destacadas para mostrar en la página principal
    try:
        # Supongamos que tienes una tabla de paquetes turísticos
        cursor = mysql.cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion_corta, precio, imagen
            FROM paquetes_turisticos
            WHERE destacado = 1
            LIMIT 4
        """)
        destacados = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Error al obtener paquetes destacados: {e}")
        destacados = []
    
    # Obtener testimonios
    try:
        cursor = mysql .cursor()
        cursor.execute("""
            SELECT c.nombre, t.comentario, t.calificacion
            FROM testimonios t
            JOIN clientes c ON t.cliente_id = c.id
            ORDER BY t.fecha DESC
            LIMIT 3
        """)
        testimonios = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Error al obtener testimonios: {e}")
        testimonios = []
        
    return render_template('public/index.html', 
                          paquetes_destacados=destacados,
                          testimonios=testimonios)

@bp.route('/promociones')
def promociones():
    """Página de promociones turísticas"""
    try:
        cursor = mysql .cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion, precio_normal, precio_oferta, 
                   fecha_inicio, fecha_fin, imagen
            FROM promociones
            WHERE fecha_fin >= CURRENT_DATE
            ORDER BY fecha_fin ASC
        """)
        promociones_activas = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Error al obtener promociones: {e}")
        promociones_activas = []
    
    return render_template('public/promociones.html', promociones=promociones_activas)

@bp.route('/destinos')
def destinos():
    """Página de destinos disponibles"""
    try:
        cursor = mysql .cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion, imagen, pais
            FROM destinos
            ORDER BY nombre ASC
        """)
        destinos_disponibles = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Error al obtener destinos: {e}")
        destinos_disponibles = []
    
    return render_template('public/destinos.html', destinos=destinos_disponibles)

@bp.route('/contacto')
def contacto():
    """Página de contacto"""
    return render_template('public/contacto.html')

@bp.route('/acerca-de')
def acerca_de():
    """Página de acerca de la empresa"""
    return render_template('public/acerca-de.html')