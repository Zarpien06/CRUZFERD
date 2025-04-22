from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql
from app.utils.decorators import rol_required
from datetime import datetime, timedelta
import random
import string

bp = Blueprint('cliente', __name__, url_prefix='/cliente')

@bp.route('/dashboard')
@rol_required('cliente')
def dashboard():
    """Dashboard del cliente con sus reservas"""
    cur = mysql.connection.cursor()
    
    # Obtener las reservas del cliente
    cur.execute("""
        SELECT r.*, p.nombre as paquete, h.nombre as hotel, 
               CONCAT(v.origen, ' - ', v.destino) as vuelo 
        FROM reservas r
        LEFT JOIN paquetes p ON r.id_paquete = p.id
        LEFT JOIN hoteles h ON r.id_hotel = h.id
        LEFT JOIN vuelos v ON r.id_vuelo = v.id
        WHERE r.id_usuario = %s
        ORDER BY r.fecha_reserva DESC
    """, [session['usuario_id']])
    
    reservas = cur.fetchall()
    cur.close()
    
    return render_template('cliente/dashboard.html', reservas=reservas)

@bp.route('/buscar', methods=['GET', 'POST'])
@rol_required('cliente')
def buscar():
    """Búsqueda de paquetes, hoteles y vuelos"""
    now = datetime.now()  # Fecha y hora actuales
    fecha_inicio_30_dias = now + timedelta(days=30) # Agregar 30 días a la fecha actual

    if request.method == 'POST':
        # Obtener datos del formulario
        destino = request.form['destino']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        
        # Guardar parámetros de búsqueda en la sesión
        session['busqueda'] = {
            'destino': destino,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }
        
        return redirect(url_for('cliente.resultados_busqueda'))
    
    return render_template('cliente/buscar.html', 
                           now=now, 
                           fecha_inicio_30_dias=fecha_inicio_30_dias,
                           timedelta=timedelta)

@bp.route('/resultados')
@rol_required('cliente')
def resultados_busqueda():
    """Muestra los resultados de la búsqueda"""
    if 'busqueda' not in session:
        flash('Debes realizar una búsqueda primero', 'warning')
        return redirect(url_for('cliente.buscar'))
    
    busqueda = session['busqueda']
    destino = busqueda['destino']
    
    cur = mysql.connection.cursor()
    
    # Buscar paquetes
    cur.execute("""
        SELECT * FROM paquetes 
        WHERE destino LIKE %s AND activo = TRUE
    """, [f'%{destino}%'])
    paquetes = cur.fetchall()
    
    # Buscar hoteles
    cur.execute("""
        SELECT * FROM hoteles 
        WHERE ubicacion LIKE %s AND disponible = TRUE
    """, [f'%{destino}%'])
    hoteles = cur.fetchall()
    
    # Buscar vuelos (simplificado)
    cur.execute("""
        SELECT * FROM vuelos 
        WHERE destino LIKE %s AND disponible = TRUE
    """, [f'%{destino}%'])
    vuelos = cur.fetchall()
    
    cur.close()
    
    return render_template('cliente/resultados.html', 
                          paquetes=paquetes, 
                          hoteles=hoteles, 
                          vuelos=vuelos, 
                          busqueda=busqueda)

@bp.route('/reservar', methods=['GET', 'POST'])
@rol_required('cliente')
def reservar():
    """Formulario de reserva"""
    if request.method == 'POST':
        # Obtener datos del formulario
        id_paquete = request.form.get('id_paquete')
        id_hotel = request.form.get('id_hotel')
        id_vuelo = request.form.get('id_vuelo')
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        num_personas = int(request.form['num_personas'])
        
        # Calcular precio total
        precio_total = 0
        cur = mysql.connection.cursor()
        
        if id_paquete:
            cur.execute("SELECT precio FROM paquetes WHERE id = %s", [id_paquete])
            precio_paquete = cur.fetchone()['precio']
            precio_total += precio_paquete * num_personas
        
        if id_hotel:
            cur.execute("SELECT precio_noche FROM hoteles WHERE id = %s", [id_hotel])
            precio_noche = cur.fetchone()['precio_noche']
            # Calcular días
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d')
            dias = (fecha_fin_obj - fecha_inicio_obj).days
            precio_total += precio_noche * dias * num_personas
        
        if id_vuelo:
            cur.execute("SELECT precio FROM vuelos WHERE id = %s", [id_vuelo])
            precio_vuelo = cur.fetchone()['precio']
            precio_total += precio_vuelo * num_personas
        
        # Almacenar en sesión para el siguiente paso
        session['reserva_temp'] = {
            'id_paquete': id_paquete,
            'id_hotel': id_hotel,
            'id_vuelo': id_vuelo,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'num_personas': num_personas,
            'precio_total': precio_total
        }
        
        cur.close()
        
        return redirect(url_for('cliente.pago'))
        
    # Obtener datos para el formulario de reserva
    id_paquete = request.args.get('paquete')
    id_hotel = request.args.get('hotel')
    id_vuelo = request.args.get('vuelo')
    
    cur = mysql.connection.cursor()
    paquete = hotel = vuelo = None
    
    if id_paquete:
        cur.execute("SELECT * FROM paquetes WHERE id = %s", [id_paquete])
        paquete = cur.fetchone()
    
    if id_hotel:
        cur.execute("SELECT * FROM hoteles WHERE id = %s", [id_hotel])
        hotel = cur.fetchone()
    
    if id_vuelo:
        cur.execute("SELECT * FROM vuelos WHERE id = %s", [id_vuelo])
        vuelo = cur.fetchone()
    
    cur.close()
    
    if not (paquete or hotel or vuelo):
        flash('Debes seleccionar al menos un servicio para reservar', 'warning')
        return redirect(url_for('cliente.resultados_busqueda'))
    
    return render_template('cliente/reserva.html', 
                          paquete=paquete, 
                          hotel=hotel, 
                          vuelo=vuelo,
                          fecha_inicio=session['busqueda']['fecha_inicio'] if 'busqueda' in session else '',
                          fecha_fin=session['busqueda']['fecha_fin'] if 'busqueda' in session else '')

@bp.route('/pago', methods=['GET', 'POST'])
@rol_required('cliente')
def pago():
    """Formulario de pago (simulado)"""
    if 'reserva_temp' not in session:
        flash('No hay información de reserva', 'warning')
        return redirect(url_for('cliente.buscar'))
    
    if request.method == 'POST':
        # Simulación de pago
        # En un sistema real aquí iría la integración con un gateway de pago
        
        # Generar código de reserva (voucher)
        ahora = datetime.now()
        letras = ''.join(random.choices(string.ascii_uppercase, k=2))
        codigo = f"RV-{ahora.strftime('%Y%m%d')}-{letras}{random.randint(1000, 9999)}"
        
        # Obtener datos de la reserva
        reserva = session['reserva_temp']
        
        # Guardar la reserva en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO reservas 
            (codigo, id_usuario, id_paquete, id_hotel, id_vuelo, fecha_inicio, fecha_fin, 
             num_personas, precio_total, estado) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmada')
        """, (
            codigo, 
            session['usuario_id'],
            reserva['id_paquete'] if reserva['id_paquete'] else None,
            reserva['id_hotel'] if reserva['id_hotel'] else None,
            reserva['id_vuelo'] if reserva['id_vuelo'] else None,
            reserva['fecha_inicio'],
            reserva['fecha_fin'],
            reserva['num_personas'],
            reserva['precio_total']
        ))
        mysql.connection.commit()
        
        # Obtener el ID de la reserva
        id_reserva = cur.lastrowid
        cur.close()
        
        # Eliminar datos temporales de la sesión
        session.pop('reserva_temp', None)
        
        # Redireccionar al voucher
        return redirect(url_for('cliente.voucher', id=id_reserva))
    
    # Obtener datos adicionales si necesarios
    reserva = session['reserva_temp']
    cur = mysql.connection.cursor()
    
    paquete = hotel = vuelo = None
    
    if reserva['id_paquete']:
        cur.execute("SELECT * FROM paquetes WHERE id = %s", [reserva['id_paquete']])
        paquete = cur.fetchone()
    
    if reserva['id_hotel']:
        cur.execute("SELECT * FROM hoteles WHERE id = %s", [reserva['id_hotel']])
        hotel = cur.fetchone()
    
    if reserva['id_vuelo']:
        cur.execute("SELECT * FROM vuelos WHERE id = %s", [reserva['id_vuelo']])
        vuelo = cur.fetchone()
    
    cur.close()
    
    return render_template('cliente/pago.html', 
                          reserva=reserva,
                          paquete=paquete,
                          hotel=hotel,
                          vuelo=vuelo)

@bp.route('/voucher/<int:id>')
@rol_required('cliente')
def voucher(id):
    """Muestra el voucher de la reserva"""
    cur = mysql.connection.cursor()
    
    # Obtener datos completos de la reserva (sin v.numero)
    cur.execute("""
        SELECT r.*, 
               p.nombre as paquete_nombre, p.destino as paquete_destino, p.descripcion as paquete_descripcion,
               h.nombre as hotel_nombre, h.ubicacion as hotel_ubicacion, h.categoria as hotel_categoria,
               v.origen as vuelo_origen, v.destino as vuelo_destino,
               v.fecha_salida, v.fecha_llegada, 
               u.nombre, u.correo
        FROM reservas r
        LEFT JOIN paquetes p ON r.id_paquete = p.id
        LEFT JOIN hoteles h ON r.id_hotel = h.id
        LEFT JOIN vuelos v ON r.id_vuelo = v.id
        JOIN usuarios u ON r.id_usuario = u.id
        WHERE r.id = %s AND r.id_usuario = %s
    """, (id, session['usuario_id']))
    
    datos_reserva = cur.fetchone()
    
    if not datos_reserva:
        flash('No se encontró la reserva solicitada', 'danger')
        return redirect(url_for('cliente.dashboard'))
    
    # Consultar los viajeros asociados a esta reserva (si existe una tabla para esto)
    viajeros = []
    try:
        cur.execute("""
            SELECT nombre, apellido
            FROM viajeros
            WHERE id_reserva = %s
        """, (id,))
        viajeros = cur.fetchall()
    except:
        pass  # Si la tabla no existe o hay error, continuamos sin viajeros
    
    cur.close()
    
    # Calcular impuestos y subtotal
    precio_total = float(datos_reserva['precio_total']) if 'precio_total' in datos_reserva else 0
    subtotal = round(precio_total / 1.16, 2)
    impuestos = round(precio_total - subtotal, 2)
    
    # Estructura del voucher
    reserva = {
        'codigo': datos_reserva.get('codigo', id),
        'fecha_creacion': datos_reserva.get('fecha_reserva', datetime.now()).strftime('%d/%m/%Y') 
            if hasattr(datos_reserva.get('fecha_reserva', datetime.now()), 'strftime') 
            else datos_reserva.get('fecha_reserva', ''),
        'ref_pago': datos_reserva.get('referencia_pago', datos_reserva.get('codigo', 'N/A')),
        'cliente': {
            'nombre': datos_reserva['nombre'],
            'apellido': datos_reserva.get('apellido', ''),
            'email': datos_reserva['correo'],
            'telefono': datos_reserva.get('telefono', 'No especificado')
        },
        'paquete_nombre': datos_reserva.get('paquete_nombre'),
        'paquete_descripcion': datos_reserva.get('paquete_descripcion', 'Descripción no disponible'),
        'hotel_nombre': datos_reserva.get('hotel_nombre'),
        'hotel_categoria': datos_reserva.get('hotel_categoria', '3'),
        'hotel_ubicacion': datos_reserva.get('hotel_ubicacion'),
        'fecha_inicio': datos_reserva.get('fecha_inicio', '').strftime('%d/%m/%Y') 
            if hasattr(datos_reserva.get('fecha_inicio', ''), 'strftime') 
            else datos_reserva.get('fecha_inicio', ''),
        'fecha_fin': datos_reserva.get('fecha_fin', '').strftime('%d/%m/%Y') 
            if hasattr(datos_reserva.get('fecha_fin', ''), 'strftime') 
            else datos_reserva.get('fecha_fin', ''),
        'tipo_habitacion': datos_reserva.get('tipo_habitacion', 'Estándar'),
        'vuelo_ruta': f"{datos_reserva.get('vuelo_origen', '')} - {datos_reserva.get('vuelo_destino', '')}" 
            if datos_reserva.get('vuelo_origen') and datos_reserva.get('vuelo_destino') 
            else '',
        'vuelo_origen': datos_reserva.get('vuelo_origen'),
        'vuelo_destino': datos_reserva.get('vuelo_destino'),
        'vuelo_fecha_ida': datos_reserva.get('fecha_salida', '').strftime('%d/%m/%Y') 
            if hasattr(datos_reserva.get('fecha_salida', ''), 'strftime') 
            else datos_reserva.get('fecha_salida', ''),
        'vuelo_hora_ida': datos_reserva.get('fecha_salida', '').strftime('%H:%M') 
            if hasattr(datos_reserva.get('fecha_salida', ''), 'strftime') 
            else '12:00',
        'vuelo_fecha_vuelta': datos_reserva.get('fecha_llegada', '').strftime('%d/%m/%Y') 
            if hasattr(datos_reserva.get('fecha_llegada', ''), 'strftime') 
            else datos_reserva.get('fecha_llegada', ''),
        'vuelo_hora_vuelta': datos_reserva.get('fecha_llegada', '').strftime('%H:%M') 
            if hasattr(datos_reserva.get('fecha_llegada', ''), 'strftime') 
            else '12:00',
        'vuelo_numero_ida': 'N/A',  # Se omite porque no existe en la tabla
        'vuelo_numero_vuelta': '',
        'num_personas': datos_reserva.get('num_personas', len(viajeros) if viajeros else 1),
        'viajeros': viajeros if viajeros else [{'nombre': datos_reserva['nombre'], 'apellido': datos_reserva.get('apellido', '')}],
        'subtotal': subtotal,
        'impuestos': impuestos,
        'precio_total': precio_total
    }
    
    fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    return render_template('cliente/voucher.html', reserva=reserva, fecha_actual=fecha_actual)
