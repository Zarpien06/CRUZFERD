-- ====================
-- SCRIPT DE ELIMINACIONES
-- ====================

-- 1. Eliminar una promoción expirada
DELETE FROM promociones
WHERE fecha_fin < CURDATE() AND id NOT IN (SELECT DISTINCT id_promocion FROM reservas WHERE id_promocion IS NOT NULL);

-- 2. Eliminar un vuelo cancelado
DELETE FROM vuelos
WHERE id = 3 AND id NOT IN (SELECT DISTINCT id_vuelo FROM reservas WHERE id_vuelo IS NOT NULL);

-- 3. Eliminar actualizaciones antiguas
DELETE FROM actualizaciones
WHERE fecha_actualizacion < DATE_SUB(CURDATE(), INTERVAL 6 MONTH);

-- 4. Eliminar un usuario inactivo
DELETE FROM usuarios
WHERE id = 10 AND id NOT IN (SELECT DISTINCT id_usuario FROM reservas);

-- 5. Eliminar un paquete discontinuado
DELETE FROM paquetes
WHERE id = 5 AND activo = FALSE AND id NOT IN (SELECT DISTINCT id_paquete FROM reservas WHERE id_paquete IS NOT NULL);
