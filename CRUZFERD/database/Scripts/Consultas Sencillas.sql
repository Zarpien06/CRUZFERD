-- ====================
-- CONSULTAS SENCILLAS
-- ====================

-- Paquetes con descuento mayor al 20%
SELECT p.nombre, p.destino, p.precio AS precio_original,
       pr.codigo, pr.descuento,
       (p.precio - (p.precio * pr.descuento / 100)) AS precio_con_descuento
FROM paquetes p
INNER JOIN promociones pr ON 
    (pr.fecha_inicio <= CURDATE() AND pr.fecha_fin >= CURDATE())
WHERE pr.descuento > 20 AND pr.activo = TRUE;

-- Reservas realizadas en el último mes
SELECT r.codigo, r.fecha_reserva, u.nombre AS cliente, p.nombre AS paquete,
       r.fecha_inicio, r.fecha_fin, r.precio_total, r.estado
FROM reservas r
INNER JOIN usuarios u ON r.id_usuario = u.id
INNER JOIN paquetes p ON r.id_paquete = p.id
WHERE r.fecha_reserva >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);

-- Vuelos con asientos disponibles
SELECT id, aerolinea, origen, destino, fecha_salida, fecha_llegada, precio
FROM vuelos
WHERE disponible = TRUE AND fecha_salida > CURDATE();

-- Hoteles con valoración mayor a 4 estrellas
SELECT id, nombre, ubicacion, categoria AS estrellas, precio_noche
FROM hoteles
WHERE categoria > 4 AND disponible = TRUE;

-- Clientes con más de 5 reservas
SELECT u.id, u.nombre, u.correo, COUNT(r.id) AS total_reservas
FROM usuarios u
INNER JOIN reservas r ON u.id = r.id_usuario
WHERE u.rol = 'cliente'
GROUP BY u.id, u.nombre, u.correo
HAVING COUNT(r.id) > 5;
