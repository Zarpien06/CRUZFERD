from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import mysql
from app.utils.decorators import rol_required
import datetime
import json

bp = Blueprint('proveedor', __name__, url_prefix='/proveedor')

@bp.route('/dashboard')
@rol_required('proveedor')
def dashboard():
    """Dashboard del proveedor con histórico de actualizaciones"""
    cur = mysql.connection.cursor()
    
    # Obtener historial de actualizaciones del proveedor
    cur.execute("""
        SELECT a.*, 
               CASE 
                   WHEN a.tipo = 'hotel' THEN h.nombre
                   WHEN a.tipo = 'vuelo' THEN CONCAT(v.origen, ' - ', v.destino)
                   WHEN a.tipo = 'paquete' THEN p.nombre
               END as nombre_item
        FROM actualizaciones a
        LEFT JOIN hoteles h ON a.tipo = 'hotel' AND a.id_item = h.id
        LEFT JOIN vuelos v ON a.tipo = 'vuelo' AND a.id_item = v.id
        LEFT JOIN paquetes p ON a.tipo = 'paquete' AND a.id_item = p.id
        WHERE a.id_proveedor = %s
        ORDER BY a.fecha_actualizacion DESC
        LIMIT 50
    """, [session['usuario_id']])
    
    actualizaciones = cur.fetchall()
    
    # Obtener resumen de disponibilidad actual
    cur.execute("""
        SELECT 
            'hoteles' as tipo,
            COUNT(*) as total,
            SUM(CASE WHEN disponible = 1 THEN 1 ELSE 0 END) as disponibles
        FROM hoteles
        UNION
        SELECT 
            'vuelos' as tipo,
            COUNT(*) as total,
            SUM(CASE WHEN disponible = 1 THEN 1 ELSE 0 END) as disponibles
        FROM vuelos
        UNION
        SELECT 
            'paquetes' as tipo,
            COUNT(*) as total,
            SUM(CASE WHEN activo = 1 THEN 1 ELSE 0 END) as disponibles
        FROM paquetes
    """)
    
    disponibilidad = cur.fetchall()
    cur.close()
    
    return render_template('proveedor/dashboard.html', 
                          actualizaciones=actualizaciones,
                          disponibilidad=disponibilidad)

@bp.route('/hoteles')
@rol_required('proveedor')
def hoteles():
    """Listado de hoteles para actualizar"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM hoteles ORDER BY nombre")
    hoteles = cur.fetchall()
    cur.close()
    
    return render_template('proveedor/hoteles.html', hoteles=hoteles)

@bp.route('/vuelos')
@rol_required('proveedor')
def vuelos():
    """Listado de vuelos para actualizar"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM vuelos ORDER BY fecha_salida")
    vuelos = cur.fetchall()
    cur.close()
    
    return render_template('proveedor/vuelos.html', vuelos=vuelos)

@bp.route('/paquetes')
@rol_required('proveedor')
def paquetes():
    """Listado de paquetes turísticos para actualizar"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM paquetes ORDER BY nombre")
    paquetes = cur.fetchall()
    cur.close()
    
    return render_template('proveedor/paquetes.html', paquetes=paquetes)

@bp.route('/actualizar/hotel/<int:id>', methods=['POST'])
@rol_required('proveedor')
def actualizar_hotel(id):
    """Actualizar disponibilidad y precio de un hotel"""
    disponible = 'disponible' in request.form
    precio = float(request.form['precio'])
    
    cur = mysql.connection.cursor()
    
    # Actualizar hotel
    cur.execute(
        "UPDATE hoteles SET disponible = %s, precio_noche = %s WHERE id = %s",
        (disponible, precio, id)
    )
    
    # Registrar actualización
    cur.execute(
        """INSERT INTO actualizaciones 
           (id_proveedor, tipo, id_item, disponible, precio) 
           VALUES (%s, 'hotel', %s, %s, %s)""",
        (session['usuario_id'], id, disponible, precio)
    )
    
    mysql.connection.commit()
    cur.close()
    
    flash('Hotel actualizado correctamente', 'success')
    return redirect(url_for('proveedor.hoteles'))

@bp.route('/actualizar/vuelo/<int:id>', methods=['POST'])
@rol_required('proveedor')
def actualizar_vuelo(id):
    """Actualizar disponibilidad y precio de un vuelo"""
    disponible = 'disponible' in request.form
    precio = float(request.form['precio'])
    
    cur = mysql.connection.cursor()
    
    # Actualizar vuelo
    cur.execute(
        "UPDATE vuelos SET disponible = %s, precio = %s WHERE id = %s",
        (disponible, precio, id)
    )
    
    # Registrar actualización
    cur.execute(
        """INSERT INTO actualizaciones 
           (id_proveedor, tipo, id_item, disponible, precio) 
           VALUES (%s, 'vuelo', %s, %s, %s)""",
        (session['usuario_id'], id, disponible, precio)
    )
    
    mysql.connection.commit()
    cur.close()
    
    flash('Vuelo actualizado correctamente', 'success')
    return redirect(url_for('proveedor.vuelos'))

@bp.route('/actualizar/paquete/<int:id>', methods=['POST'])
@rol_required('proveedor')
def actualizar_paquete(id):
    """Actualizar disponibilidad y precio de un paquete"""
    activo = 'activo' in request.form
    precio = float(request.form['precio'])
    
    cur = mysql.connection.cursor()
    
    # Actualizar paquete
    cur.execute(
        "UPDATE paquetes SET activo = %s, precio = %s WHERE id = %s",
        (activo, precio, id)
    )
    
    # Registrar actualización
    cur.execute(
        """INSERT INTO actualizaciones 
           (id_proveedor, tipo, id_item, disponible, precio) 
           VALUES (%s, 'paquete', %s, %s, %s)""",
        (session['usuario_id'], id, activo, precio)
    )
    
    mysql.connection.commit()
    cur.close()
    
    flash('Paquete actualizado correctamente', 'success')
    return redirect(url_for('proveedor.paquetes'))

@bp.route('/api/actualizar', methods=['POST'])
@rol_required('proveedor')
def api_actualizar():
    """API para actualizar disponibilidad por JSON"""
    try:
        # Validar que sea JSON
        if not request.is_json:
            return jsonify({"status": "error", "message": "Se requiere JSON"}), 400
        
        data = request.get_json()
        
        # Validar datos mínimos
        if not all(k in data for k in ["tipo", "id", "disponible"]):
            return jsonify({"status": "error", "message": "Datos incompletos"}), 400
        
        tipo = data.get("tipo")
        id_item = data.get("id")
        disponible = data.get("disponible")
        precio = data.get("precio")
        
        if tipo not in ["hotel", "vuelo", "paquete"]:
            return jsonify({"status": "error", "message": "Tipo inválido"}), 400
        
        cur = mysql.connection.cursor()
        
        # Actualizar según tipo
        if tipo == "hotel":
            if precio:
                cur.execute(
                    "UPDATE hoteles SET disponible = %s, precio_noche = %s WHERE id = %s",
                    (disponible, precio, id_item)
                )
            else:
                cur.execute(
                    "UPDATE hoteles SET disponible = %s WHERE id = %s",
                    (disponible, id_item)
                )
        elif tipo == "vuelo":
            if precio:
                cur.execute(
                    "UPDATE vuelos SET disponible = %s, precio = %s WHERE id = %s",
                    (disponible, precio, id_item)
                )
            else:
                cur.execute(
                    "UPDATE vuelos SET disponible = %s WHERE id = %s",
                    (disponible, id_item)
                )
        elif tipo == "paquete":
            campo_disponible = "activo" if tipo == "paquete" else "disponible"
            if precio:
                cur.execute(
                    f"UPDATE paquetes SET {campo_disponible} = %s, precio = %s WHERE id = %s",
                    (disponible, precio, id_item)
                )
            else:
                cur.execute(
                    f"UPDATE paquetes SET {campo_disponible} = %s WHERE id = %s",
                    (disponible, id_item)
                )
        
        # Registrar actualización
        cur.execute(
            """INSERT INTO actualizaciones 
               (id_proveedor, tipo, id_item, disponible, precio) 
               VALUES (%s, %s, %s, %s, %s)""",
            (session['usuario_id'], tipo, id_item, disponible, precio)
        )
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"status": "ok", "message": "Actualización exitosa"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/carga-masiva', methods=['GET', 'POST'])
@rol_required('proveedor')
def carga_masiva():
    """Formulario para carga masiva de actualizaciones"""
    if request.method == 'POST':
        try:
            # Verificar si hay archivo
            if 'archivo_json' not in request.files:
                flash('No se encontró ningún archivo', 'danger')
                return redirect(request.url)
            
            archivo = request.files['archivo_json']
            
            # Si no se selecciona archivo
            if archivo.filename == '':
                flash('No se seleccionó ningún archivo', 'danger')
                return redirect(request.url)
            
            # Procesar archivo JSON
            if archivo and archivo.filename.endswith('.json'):
                contenido = archivo.read()
                datos = json.loads(contenido)
                
                # Validar estructura de datos
                if not isinstance(datos, list):
                    flash('El archivo debe contener un arreglo de objetos', 'danger')
                    return redirect(request.url)
                
                actualizaciones_ok = 0
                actualizaciones_error = 0
                
                cur = mysql.connection.cursor()
                
                for item in datos:
                    try:
                        tipo = item.get('tipo')
                        id_item = item.get('id')
                        disponible = item.get('disponible')
                        precio = item.get('precio')
                        
                        if not all([tipo, id_item, disponible is not None]):
                            actualizaciones_error += 1
                            continue
                        
                        # Actualizar según tipo
                        if tipo == "hotel":
                            if precio:
                                cur.execute(
                                    "UPDATE hoteles SET disponible = %s, precio_noche = %s WHERE id = %s",
                                    (disponible, precio, id_item)
                                )
                            else:
                                cur.execute(
                                    "UPDATE hoteles SET disponible = %s WHERE id = %s",
                                    (disponible, id_item)
                                )
                        elif tipo == "vuelo":
                            if precio:
                                cur.execute(
                                    "UPDATE vuelos SET disponible = %s, precio = %s WHERE id = %s",
                                    (disponible, precio, id_item)
                                )
                            else:
                                cur.execute(
                                    "UPDATE vuelos SET disponible = %s WHERE id = %s",
                                    (disponible, id_item)
                                )
                        elif tipo == "paquete":
                            campo_disponible = "activo" if tipo == "paquete" else "disponible"
                            if precio:
                                cur.execute(
                                    f"UPDATE paquetes SET {campo_disponible} = %s, precio = %s WHERE id = %s",
                                    (disponible, precio, id_item)
                                )
                            else:
                                cur.execute(
                                    f"UPDATE paquetes SET {campo_disponible} = %s WHERE id = %s",
                                    (disponible, id_item)
                                )
                        
                        # Registrar actualización
                        cur.execute(
                            """INSERT INTO actualizaciones 
                               (id_proveedor, tipo, id_item, disponible, precio) 
                               VALUES (%s, %s, %s, %s, %s)""",
                            (session['usuario_id'], tipo, id_item, disponible, precio)
                        )
                        
                        actualizaciones_ok += 1
                    except Exception as e:
                        actualizaciones_error += 1
                
                mysql.connection.commit()
                cur.close()
                
                flash(f'Proceso completado. Actualizaciones exitosas: {actualizaciones_ok}. Errores: {actualizaciones_error}', 'info')
            else:
                flash('El archivo debe tener extensión .json', 'danger')
                
        except Exception as e:
            flash(f'Error al procesar el archivo: {str(e)}', 'danger')
    
    return render_template('proveedor/carga_masiva.html')