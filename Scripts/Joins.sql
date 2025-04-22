-- ====================
-- CONSULTAS CON JOINS
-- ====================

-- Paquetes con su hotel y vuelo incluido
SELECT p.nombre AS paquete, p.destino, p.precio AS precio_paquete,
       h.nombre AS hotel, h.categoria AS estrellas, h.precio_noche,
       v.aerolinea, v.origen, v.destino, v.fecha_salida, v.fecha_llegada, v.precio AS precio_vuelo
FROM paquetes p
INNER JOIN hoteles h ON p.destino = h.ubicacion
INNER JOIN vuelos v ON p.destino = v.destino;

-- Reservas completas con información de cliente y paquete
SELECT r.codigo AS codigo_reserva, r.fecha_inicio, r.fecha_fin, r.precio_total, r.estado,
       u.nombre AS cliente, u.correo,
       p.nombre AS paquete, p.destino, p.duracion
FROM reservas r
INNER JOIN usuarios u ON r.id_usuario = u.id
INNER JOIN paquetes p ON r.id_paquete = p.id;

-- Vuelos con información de aerolínea y aeropuertos
SELECT v.id, v.aerolinea, v.origen AS aeropuerto_origen, v.destino AS aeropuerto_destino,
       v.fecha_salida, v.fecha_llegada, v.precio, v.disponible,
       TIMESTAMPDIFF(HOUR, v.fecha_salida, v.fecha_llegada) AS duracion_horas
FROM vuelos v;

-- Promociones aplicables a paquetes específicos
SELECT p.nombre AS paquete, p.destino, p.precio AS precio_original,
       pr.codigo AS codigo_promocion, pr.descuento,
       (p.precio - (p.precio * pr.descuento / 100)) AS precio_con_descuento
FROM paquetes p
INNER JOIN promociones pr ON 
    (pr.fecha_inicio <= CURDATE() AND pr.fecha_fin >= CURDATE())
    AND (
        (p.destino = 'Europa' AND pr.codigo = 'EUROPA25') OR
        (p.destino IN ('Cancún', 'Punta Cana') AND pr.codigo = 'CARIBE30') OR
        (p.destino = 'Japón' AND pr.codigo = 'ASIA20') OR
        (p.destino = 'Kenia' AND pr.codigo = 'AFRICA15') OR
        pr.codigo = 'VERANO2025'
    )
WHERE pr.activo = TRUE;

-- Habitaciones reservadas con información de hotel y cliente
SELECT r.codigo AS codigo_reserva, r.fecha_inicio, r.fecha_fin, r.num_personas,
       h.nombre AS hotel, h.ubicacion, h.categoria AS estrellas,
       u.nombre AS cliente, u.correo
FROM reservas r
INNER JOIN hoteles h ON r.id_hotel = h.id
INNER JOIN usuarios u ON r.id_usuario = u.id;