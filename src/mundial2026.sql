CREATE DATABASE mundial2026;
USE mundial2026;

-- USUARIOS
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100),
    puntos INT DEFAULT 0
);

-- EQUIPOS
CREATE TABLE equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    grupo CHAR(1)
);

-- PARTIDOS
CREATE TABLE partidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_local INT,
    equipo_visitante INT,
    goles_local INT,
    goles_visitante INT,
    fase VARCHAR(50)
);

-- PREDICCIONES
CREATE TABLE predicciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    partido_id INT,
    goles_local INT,
    goles_visitante INT
);

-- MEJORES TERCEROS
CREATE TABLE terceros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    equipo_id INT
);

-- PREDICCION RONDAS
CREATE TABLE prediccion_rondas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    equipo_id INT,
    ronda VARCHAR(20)
);

INSERT INTO usuarios (nombre, email) VALUES
('Ana', 'ana@test.com'),
('Luis', 'luis@test.com');

INSERT INTO equipos (nombre, grupo) VALUES
('Colombia','A'),
('Brasil','A'),
('Argentina','B'),
('Francia','B');

INSERT INTO partidos (equipo_local, equipo_visitante, fase) VALUES
(1,2,'grupos'),
(3,4,'grupos');