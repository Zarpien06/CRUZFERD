-- ====================
-- SCRIPT DE MODIFICACIONES
-- ====================

-- 1. Actualizar el precio de un paquete
UPDATE paquetes
SET precio = 1350.00, descripcion = 'Paquete todo incluido premium con actividades acuáticas y tours'
WHERE id = 1;

-- 2. Cambiar el rol de un usuario
UPDATE usuarios
SET rol = 'agente'
WHERE id = 5;

-- 3. Extender la fecha de validez de una promoción
UPDATE promociones
SET fecha_fin = '2025-12-31', descuento = 35.00
WHERE codigo = 'CARIBE30';

-- 4. Actualizar el estado de una reserva
UPDATE reservas
SET estado = 'confirmada'
WHERE codigo = 'RES-003';

-- 5. Cambiar la disponibilidad y precio de un hotel
UPDATE hoteles
SET disponible = FALSE, precio_noche = 300.00
WHERE id = 2;
