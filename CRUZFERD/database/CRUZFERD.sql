-- Creación de la base de datos
CREATE DATABASE IF NOT EXISTS CRUZFERD;
USE CRUZFERD;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    rol ENUM('cliente', 'agente', 'proveedor') NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de paquetes turísticos
CREATE TABLE IF NOT EXISTS paquetes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    destino VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    duracion INT NOT NULL COMMENT 'Duración en días',
    imagen VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de hoteles
CREATE TABLE IF NOT EXISTS hoteles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    ubicacion VARCHAR(100) NOT NULL,
    categoria INT NOT NULL COMMENT 'Estrellas del hotel (1-5)',
    precio_noche DECIMAL(10, 2) NOT NULL,
    imagen VARCHAR(255),
    disponible BOOLEAN DEFAULT TRUE
);

-- Tabla de vuelos
CREATE TABLE IF NOT EXISTS vuelos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aerolinea VARCHAR(100) NOT NULL,
    origen VARCHAR(100) NOT NULL,
    destino VARCHAR(100) NOT NULL,
    fecha_salida DATETIME NOT NULL,
    fecha_llegada DATETIME NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    disponible BOOLEAN DEFAULT TRUE
);

-- Tabla de promociones
CREATE TABLE IF NOT EXISTS promociones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    descripcion TEXT,
    descuento DECIMAL(5, 2) NOT NULL COMMENT 'Porcentaje de descuento',
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de reservas
CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE COMMENT 'Código de voucher',
    id_usuario INT NOT NULL,
    id_paquete INT,
    id_hotel INT,
    id_vuelo INT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    num_personas INT NOT NULL DEFAULT 1,
    precio_total DECIMAL(10, 2) NOT NULL,
    id_promocion INT,
    estado ENUM('pendiente', 'confirmada', 'cancelada') DEFAULT 'pendiente',
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_paquete) REFERENCES paquetes(id),
    FOREIGN KEY (id_hotel) REFERENCES hoteles(id),
    FOREIGN KEY (id_vuelo) REFERENCES vuelos(id),
    FOREIGN KEY (id_promocion) REFERENCES promociones(id)
);

-- Tabla para actualización de disponibilidad
CREATE TABLE IF NOT EXISTS actualizaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    tipo ENUM('hotel', 'vuelo', 'paquete') NOT NULL,
    id_item INT NOT NULL COMMENT 'ID del hotel, vuelo o paquete',
    disponible BOOLEAN NOT NULL,
    precio DECIMAL(10, 2),
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_proveedor) REFERENCES usuarios(id)
);

-- Insertar datos de ejemplo (opcional pero útil para pruebas)

-- Usuarios de prueba (contraseña: 'password')
INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES
('Cliente Demo', 'cliente@demo.com', '$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwlOC.KmfsbFEs1jxP4r.L9PiYTW', 'cliente'),
('Agente Demo', 'agente@demo.com', '$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwlOC.KmfsbFEs1jxP4r.L9PiYTW', 'agente'),
('Proveedor Demo', 'proveedor@demo.com', '$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwlOC.KmfsbFEs1jxP4r.L9PiYTW', 'proveedor');

-- Paquetes turísticos
INSERT INTO paquetes (nombre, descripcion, destino, precio, duracion, imagen) VALUES
('Aventura en Cancún', 'Disfruta de las playas y la cultura maya', 'Cancún, México', 1200.00, 7, 'cancun.jpg'),
('Tour por Europa', 'Visita las principales ciudades europeas', 'Europa', 3500.00, 15, 'europa.jpg'),
('Relax en Bali', 'Descanso y bienestar en las playas de Bali', 'Bali, Indonesia', 1800.00, 10, 'bali.jpg');

-- Hoteles
INSERT INTO hoteles (nombre, descripcion, ubicacion, categoria, precio_noche) VALUES
('Gran Hotel Cancún', 'Hotel 5 estrellas con vista al mar', 'Cancún, México', 5, 200.00),
('Hostería Romana', 'Céntrico hotel en el corazón de Roma', 'Roma, Italia', 4, 150.00),
('Bali Paradise', 'Resort en la playa de Kuta', 'Bali, Indonesia', 5, 180.00);

-- Vuelos
INSERT INTO vuelos (aerolinea, origen, destino, fecha_salida, fecha_llegada, precio) VALUES
('Aeroméxico', 'Ciudad de México', 'Cancún', '2025-05-15 08:00:00', '2025-05-15 10:30:00', 250.00),
('Iberia', 'Madrid', 'Roma', '2025-06-20 14:00:00', '2025-06-20 16:30:00', 320.00),
('Qatar Airways', 'Doha', 'Bali', '2025-07-10 23:00:00', '2025-07-11 14:00:00', 580.00);

-- Promociones
INSERT INTO promociones (codigo, descripcion, descuento, fecha_inicio, fecha_fin) VALUES
('VERANO2025', 'Descuento de verano', 15.00, '2025-06-01', '2025-08-31'),
('FLASH25', 'Oferta relámpago', 25.00, '2025-05-01', '2025-05-07');