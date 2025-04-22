-- ====================
-- CONSULTAS ADICIONALES PARA EL CASO DE ESTUDIO
-- ====================

-- Ingresos totales por mes
SELECT 
    YEAR(fecha_reserva) AS año,
    MONTH(fecha_reserva) AS mes,
    SUM(precio_total) AS ingresos_totales,
    COUNT(*) AS numero_reservas
FROM reservas
GROUP BY YEAR(fecha_reserva), MONTH(fecha_reserva)
ORDER BY año DESC, mes DESC;

-- Top 5 destinos más populares
SELECT 
    p.destino,
    COUNT(r.id) AS total_reservas,
    SUM(r.precio_total) AS ingresos_totales
FROM reservas r
JOIN paquetes p ON r.id_paquete = p.id
GROUP BY p.destino
ORDER BY total_reservas DESC
LIMIT 5;

-- Efectividad de las promociones
SELECT 
    p.codigo,
    p.descuento,
    COUNT(r.id) AS reservas_con_promocion,
    SUM(r.precio_total) AS ingresos_con_promocion
FROM promociones p
LEFT JOIN reservas r ON p.id = r.id_promocion
GROUP BY p.codigo, p.descuento
ORDER BY reservas_con_promocion DESC;

-- Rendimiento de agentes de ventas
SELECT 
    u.nombre AS agente,
    COUNT(r.id) AS reservas_gestionadas,
    SUM(r.precio_total) AS ventas_totales
FROM usuarios u
JOIN reservas r ON u.id = r.id_usuario
WHERE u.rol = 'agente'
GROUP BY u.nombre
ORDER BY ventas_totales DESC;

-- Ocupación de hoteles por temporada
SELECT 
    h.nombre AS hotel,
    h.ubicacion,
    CASE 
        WHEN MONTH(r.fecha_inicio) BETWEEN 6 AND 8 THEN 'Verano'
        WHEN MONTH(r.fecha_inicio) BETWEEN 9 AND 11 THEN 'Otoño'
        WHEN MONTH(r.fecha_inicio) = 12 OR MONTH(r.fecha_inicio) BETWEEN 1 AND 2 THEN 'Invierno'
        ELSE 'Primavera'
    END AS temporada,
    COUNT(*) AS total_reservas
FROM reservas r
JOIN hoteles h ON r.id_hotel = h.id
GROUP BY h.nombre, h.ubicacion, temporada
ORDER BY h.nombre, temporada;

-- Duración promedio de estadía por destino
SELECT 
    p.destino,
    AVG(DATEDIFF(r.fecha_fin, r.fecha_inicio)) AS duracion_promedio_dias
FROM reservas r
JOIN paquetes p ON r.id_paquete = p.id
GROUP BY p.destino
ORDER BY duracion_promedio_dias DESC;

-- Tendencia de reservas en los últimos 12 meses
SELECT 
    DATE_FORMAT(fecha_reserva, '%Y-%m') AS mes,
    COUNT(*) AS total_reservas,
    SUM(precio_total) AS ingresos_totales
FROM reservas
WHERE fecha_reserva >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY DATE_FORMAT(fecha_reserva, '%Y-%m')
ORDER BY mes;

-- Análisis de cancelaciones
SELECT 
    p.destino,
    COUNT(CASE WHEN r.estado = 'cancelada' THEN 1 END) AS cancelaciones,
    COUNT(*) AS total_reservas,
    (COUNT(CASE WHEN r.estado = 'cancelada' THEN 1 END) / COUNT(*)) * 100 AS porcentaje_cancelacion
FROM reservas r
JOIN paquetes p ON r.id_paquete = p.id
GROUP BY p.destino
ORDER BY porcentaje_cancelacion DESC;

-- Análisis de precios por temporada
SELECT 
    CASE 
        WHEN MONTH(fecha_inicio) BETWEEN 6 AND 8 THEN 'Verano'
        WHEN MONTH(fecha_inicio) BETWEEN 9 AND 11 THEN 'Otoño'
        WHEN MONTH(fecha_inicio) = 12 OR MONTH(fecha_inicio) BETWEEN 1 AND 2 THEN 'Invierno'
        ELSE 'Primavera'
    END AS temporada,
    AVG(precio_total / num_personas) AS precio_promedio_por_persona
FROM reservas
GROUP BY temporada
ORDER BY precio_promedio_por_persona DESC;

-- Reporte de clientes frecuentes
SELECT 
    u.id,
    u.nombre,
    u.correo,
    COUNT(r.id) AS total_reservas,
    SUM(r.precio_total) AS gasto_total,
    MAX(r.fecha_reserva) AS ultima_reserva
FROM usuarios u
JOIN reservas r ON u.id = r.id_usuario
WHERE u.rol = 'cliente'
GROUP BY u.id, u.nombre, u.correo
HAVING COUNT(r.id) >= 3
ORDER BY gasto_total DESC;