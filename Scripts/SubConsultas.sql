-- ====================
-- SUBCONSULTAS
-- ====================

-- Paquetes con precio superior al promedio
SELECT id, nombre, destino, precio, duracion
FROM paquetes
WHERE precio > (SELECT AVG(precio) FROM paquetes)
ORDER BY precio;

-- Clientes que no han viajado en el último año
SELECT id, nombre, correo
FROM usuarios
WHERE rol = 'cliente' AND id NOT IN (
    SELECT DISTINCT id_usuario
    FROM reservas
    WHERE fecha_inicio >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    AND estado = 'confirmada'
);

-- Vuelos con ocupación superior al 80%
-- Asumiendo que tenemos un máximo de asientos por vuelo (no está en el esquema original)
-- Esta consulta es conceptual y necesitaría adaptarse a la estructura real
SELECT v.id, v.aerolinea, v.origen, v.destino, v.fecha_salida
FROM vuelos v
WHERE (
    SELECT COUNT(*)
    FROM reservas r
    WHERE r.id_vuelo = v.id AND r.estado != 'cancelada'
) > (SELECT COUNT(*) * 0.8 FROM reservas WHERE id_vuelo = v.id);

-- Hoteles con todas sus habitaciones reservadas en una fecha
-- Asumiendo que tenemos un máximo de habitaciones por hotel (no está en el esquema original)
-- Esta consulta es conceptual y necesitaría adaptarse a la estructura real
SELECT h.id, h.nombre, h.ubicacion
FROM hoteles h
WHERE (
    SELECT COUNT(*)
    FROM reservas r
    WHERE r.id_hotel = h.id
    AND '2025-07-15' BETWEEN r.fecha_inicio AND r.fecha_fin
    AND r.estado != 'cancelada'
) >= 10; -- Asumiendo 10 habitaciones disponibles por hotel

-- Promociones que no han sido aplicadas
SELECT p.id, p.codigo, p.descuento, p.fecha_inicio, p.fecha_fin
FROM promociones p
WHERE p.id NOT IN (
    SELECT DISTINCT id_promocion
    FROM reservas
    WHERE id_promocion IS NOT NULL
);
