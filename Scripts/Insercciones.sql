-- ====================
-- SCRIPT DE INSERCIONES
-- ====================

USE CRUZFERD;

-- Insertando usuarios
INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES
('Juan Pérez', 'juan@gmail.com', 'pass123', 'cliente'),
('María López', 'maria@gmail.com', 'pass456', 'cliente'),
('Carlos Rodríguez', 'carlos@gmail.com', 'pass789', 'cliente'),
('Ana Martínez', 'ana@gmail.com', 'passabc', 'cliente'),
('Pedro Sánchez', 'pedro@gmail.com', 'passdef', 'cliente'),
('Laura García', 'laura@agencia.com', 'agente123', 'agente'),
('Miguel Torres', 'miguel@agencia.com', 'agente456', 'agente'),
('Elena Castro', 'elena@hotel.com', 'prov123', 'proveedor'),
('Roberto Morales', 'roberto@aerolinea.com', 'prov456', 'proveedor'),
('Sofia Jiménez', 'sofia@touroperador.com', 'prov789', 'proveedor');

-- Insertando paquetes turísticos
INSERT INTO paquetes (nombre, descripcion, destino, precio, duracion, imagen) VALUES
('Aventura en Cancún', 'Paquete todo incluido con actividades acuáticas', 'Cancún', 1200.00, 7, 'cancun.jpg'),
('Tour por Europa', 'Visita 5 países europeos en 15 días', 'Europa', 3500.00, 15, 'europa.jpg'),
('Descanso en Punta Cana', 'Vacaciones relajantes en el Caribe', 'Punta Cana', 1500.00, 5, 'puntacana.jpg'),
('Maravillas de Japón', 'Conoce la cultura y tecnología japonesa', 'Japón', 2800.00, 10, 'japon.jpg'),
('Safari Africano', 'Aventura en la sabana africana', 'Kenia', 2200.00, 8, 'safari.jpg');

-- Insertando hoteles
INSERT INTO hoteles (nombre, descripcion, ubicacion, categoria, precio_noche, imagen) VALUES
('Grand Oasis', 'Resort todo incluido frente al mar', 'Cancún', 5, 250.00, 'oasis.jpg'),
('Hotel Continental', 'Elegante hotel en el centro de la ciudad', 'París', 4, 180.00, 'continental.jpg'),
('Palacio Caribeño', 'Lujo tropical con múltiples piscinas', 'Punta Cana', 5, 220.00, 'palacio.jpg'),
('Sakura Inn', 'Hotel tradicional japonés', 'Tokio', 3, 120.00, 'sakura.jpg'),
('Safari Lodge', 'Hospedaje cerca de la reserva natural', 'Nairobi', 4, 190.00, 'lodge.jpg');

-- Insertando vuelos
INSERT INTO vuelos (aerolinea, origen, destino, fecha_salida, fecha_llegada, precio) VALUES
('Aeroméxico', 'Ciudad de México', 'Cancún', '2025-05-15 08:00:00', '2025-05-15 10:30:00', 250.00),
('Air France', 'Ciudad de México', 'París', '2025-06-20 23:00:00', '2025-06-21 18:30:00', 950.00),
('American Airlines', 'Ciudad de México', 'Punta Cana', '2025-07-05 09:15:00', '2025-07-05 14:45:00', 420.00),
('Japan Airlines', 'Ciudad de México', 'Tokio', '2025-08-10 22:30:00', '2025-08-12 05:45:00', 1100.00),
('Kenya Airways', 'Ciudad de México', 'Nairobi', '2025-09-15 21:00:00', '2025-09-16 18:30:00', 1300.00);

-- Insertando promociones
INSERT INTO promociones (codigo, descripcion, descuento, fecha_inicio, fecha_fin) VALUES
('VERANO2025', 'Descuento de verano en todos los destinos', 15.00, '2025-06-01', '2025-08-31'),
('EUROPA25', 'Descuento especial para destinos europeos', 25.00, '2025-05-01', '2025-07-31'),
('CARIBE30', 'Súper promoción para el Caribe', 30.00, '2025-04-15', '2025-06-30'),
('ASIA20', 'Descuento para destinos asiáticos', 20.00, '2025-07-01', '2025-10-31'),
('AFRICA15', 'Promoción para safaris y aventuras', 15.00, '2025-08-01', '2025-11-30');

-- Insertando reservas
INSERT INTO reservas (codigo, id_usuario, id_paquete, id_hotel, id_vuelo, fecha_inicio, fecha_fin, num_personas, precio_total, id_promocion, estado) VALUES
('RES-001', 1, 1, 1, 1, '2025-05-15', '2025-05-22', 2, 2400.00, 1, 'confirmada'),
('RES-002', 2, 2, 2, 2, '2025-06-20', '2025-07-05', 1, 3500.00, 2, 'confirmada'),
('RES-003', 3, 3, 3, 3, '2025-07-05', '2025-07-10', 3, 4500.00, 3, 'pendiente'),
('RES-004', 4, 4, 4, 4, '2025-08-10', '2025-08-20', 2, 5600.00, 4, 'confirmada'),
('RES-005', 5, 5, 5, 5, '2025-09-15', '2025-09-23', 4, 8800.00, 5, 'pendiente'),
('RES-006', 1, 3, 3, 3, '2025-10-10', '2025-10-15', 2, 3000.00, 3, 'confirmada'),
('RES-007', 2, 4, 4, 4, '2025-11-05', '2025-11-15', 1, 2800.00, 4, 'confirmada'),
('RES-008', 3, 2, 2, 2, '2025-12-20', '2026-01-04', 2, 7000.00, 2, 'pendiente'),
('RES-009', 1, 5, 5, 5, '2026-01-15', '2026-01-23', 3, 6600.00, 5, 'confirmada'),
('RES-010', 4, 1, 1, 1, '2026-02-10', '2026-02-17', 2, 2400.00, 1, 'pendiente');

-- Insertando actualizaciones
INSERT INTO actualizaciones (id_proveedor, tipo, id_item, disponible, precio) VALUES
(8, 'hotel', 1, TRUE, 270.00),
(8, 'hotel', 3, TRUE, 240.00),
(9, 'vuelo', 1, TRUE, 270.00),
(9, 'vuelo', 3, FALSE, NULL),
(10, 'paquete', 1, TRUE, 1300.00);