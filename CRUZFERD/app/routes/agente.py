from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql
from app.utils.decorators import rol_required
import datetime

bp = Blueprint('agente', __name__, url_prefix='/agente')

@bp.route('/dashboard')
@rol_required('agente')
def dashboard():
    """Dashboard del agente con métricas"""
    cur = mysql.connection.cursor()
    
    # Total de ventas por mes
    cur.execute("""
        SELECT 
            DATE_FORMAT(fecha_reserva, '%Y-%m') as mes,
            SUM(precio_total) as total_ventas,
            COUNT(*) as cantidad_reservas
        FROM reservas
        WHERE estado = 'confirmada'
        GROUP BY DATE_FORMAT(fecha_reserva, '%Y-%m')
        ORDER BY mes DESC
        LIMIT 6
    """)
    ventas_mensuales = cur.fetchall()
    
    # Paquetes más vendidos
    cur.execute("""
        SELECT 
            p.nombre,
            COUNT(*) as cantidad,
            SUM(r.precio_total) as total_ventas
        FROM reservas r
        JOIN paquetes p ON r.id_paquete = p.id
        WHERE r.estado = 'confirmada'
        GROUP BY p.id
        ORDER BY cantidad DESC
        LIMIT 5
    """)
    paquetes_top = cur.fetchall()
    
    # Destinos más populares
    cur.execute("""
        SELECT 
            p.destino,
            COUNT(*) as cantidad
        FROM reservas r
        JOIN paquetes p ON r.id_paquete = p.id
        WHERE r.estado = 'confirmada'
        GROUP BY p.destino
        ORDER BY cantidad DESC
        LIMIT 5
    """)
    destinos_top = cur.fetchall()
    
    # Reservas recientes
    cur.execute("""
        SELECT r.*, 
               u.nombre as cliente,
               p.nombre as paquete,
               h.nombre as hotel,
               CONCAT(v.origen, ' - ', v.destino) as vuelo
        FROM reservas r
        JOIN usuarios u ON r.id_usuario = u.id
        LEFT JOIN paquetes p ON r.id_paquete = p.id
        LEFT JOIN hoteles h ON r.id_hotel = h.id
        LEFT JOIN vuelos v ON r.id_vuelo = v.id
        ORDER BY r.fecha_reserva DESC
        LIMIT 10
    """)
    reservas_recientes = cur.fetchall()
    
    cur.close()
    
    return render_template('agente/dashboard.html',
                          ventas_mensuales=ventas_mensuales,
                          paquetes_top=paquetes_top,
                          destinos_top=destinos_top,
                          reservas_recientes=reservas_recientes)

@bp.route('/reservas')
@rol_required('agente')
def reservas():
    """Listado de todas las reservas con filtros"""
    # Filtros
    estado = request.args.get('estado', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    cur = mysql.connection.cursor()
    
    # Consulta base
    query = """
        SELECT r.*, 
               u.nombre as cliente,
               p.nombre as paquete,
               h.nombre as hotel,
               CONCAT(v.origen, ' - ', v.destino) as vuelo
        FROM reservas r
        JOIN usuarios u ON r.id_usuario = u.id
        LEFT JOIN paquetes p ON r.id_paquete = p.id
        LEFT JOIN hoteles h ON r.id_hotel = h.id
        LEFT JOIN vuelos v ON r.id_vuelo = v.id
    """
    
    # Añadir filtros si existen
    where_clauses = []
    params = []
    
    if estado:
        where_clauses.append("r.estado = %s")
        params.append(estado)
    
    if fecha_inicio:
        where_clauses.append("r.fecha_inicio >= %s")
        params.append(fecha_inicio)
    
    if fecha_fin:
        where_clauses.append("r.fecha_fin <= %s")
        params.append(fecha_fin)
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY r.fecha_reserva DESC"
    
    cur.execute(query, params)
    reservas = cur.fetchall()
    cur.close()
    
    return render_template('agente/reservas.html', 
                          reservas=reservas, 
                          estado=estado,
                          fecha_inicio=fecha_inicio, 
                          fecha_fin=fecha_fin)

@bp.route('/reservas/<int:id>')
@rol_required('agente')
def ver_reserva(id):
    """Ver detalles de una reserva específica"""
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT r.*, 
               u.nombre as cliente, u.correo as correo_cliente,
               p.nombre as paquete_nombre, p.descripcion as paquete_descripcion,
               h.nombre as hotel_nombre, h.descripcion as hotel_descripcion,
               v.aerolinea, v.origen, v.destino, v.fecha_salida, v.fecha_llegada
        FROM reservas r
        JOIN usuarios u ON r.id_usuario = u.id
        LEFT JOIN paquetes p ON r.id_paquete = p.id
        LEFT JOIN hoteles h ON r.id_hotel = h.id
        LEFT JOIN vuelos v ON r.id_vuelo = v.id
        WHERE r.id = %s
    """, [id])
    
    reserva = cur.fetchone()
    cur.close()
    
    if not reserva:
        flash('No se encontró la reserva solicitada', 'danger')
        return redirect(url_for('agente.reservas'))
    
    return render_template('agente/ver_reserva.html', reserva=reserva)

@bp.route('/reservas/<int:id>/actualizar', methods=['POST'])
@rol_required('agente')
def actualizar_reserva(id):
    """Actualizar estado de una reserva"""
    estado = request.form.get('estado')
    
    if not estado or estado not in ['pendiente', 'confirmada', 'cancelada']:
        flash('Estado inválido', 'danger')
        return redirect(url_for('agente.ver_reserva', id=id))
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE reservas SET estado = %s WHERE id = %s", (estado, id))
    mysql.connection.commit()
    cur.close()
    
    flash('Estado de la reserva actualizado correctamente', 'success')
    return redirect(url_for('agente.ver_reserva', id=id))

@bp.route('/promociones', methods=['GET', 'POST'])
@rol_required('agente')
def promociones():
    """Gestionar promociones"""
    if request.method == 'POST':
        codigo = request.form['codigo']
        descripcion = request.form['descripcion']
        descuento = float(request.form['descuento'])
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        
        cur = mysql.connection.cursor()
        
        # Verificar si el código ya existe
        cur.execute("SELECT id FROM promociones WHERE codigo = %s", [codigo])
        promo_existente = cur.fetchone()
        
        if promo_existente:
            flash('El código de promoción ya existe', 'warning')
        else:
            cur.execute("""
                INSERT INTO promociones 
                (codigo, descripcion, descuento, fecha_inicio, fecha_fin) 
                VALUES (%s, %s, %s, %s, %s)
            """, (codigo, descripcion, descuento, fecha_inicio, fecha_fin))
            mysql.connection.commit()
            flash('Promoción creada correctamente', 'success')
        
        cur.close()
    
    # Listar promociones
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM promociones ORDER BY fecha_inicio DESC")
    promociones = cur.fetchall()
    cur.close()
    
    return render_template('agente/promociones.html', promociones=promociones)

@bp.route('/promociones/<int:id>/toggle', methods=['POST'])
@rol_required('agente')
def toggle_promocion(id):
    """Activar/desactivar promoción"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT activo FROM promociones WHERE id = %s", [id])
    promo = cur.fetchone()
    
    if promo:
        nuevo_estado = not promo['activo']
        cur.execute("UPDATE promociones SET activo = %s WHERE id = %s", (nuevo_estado, id))
        mysql.connection.commit()
        flash('Estado de la promoción actualizado', 'success')
    else:
        flash('Promoción no encontrada', 'danger')
    
    cur.close()
    return redirect(url_for('agente.promociones'))