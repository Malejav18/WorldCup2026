CREATE DATABASE mundial;
USE mundial;

-- USUARIOS
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100)
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

-- TERCEROS
CREATE TABLE terceros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    equipo_id INT
);

-- CLASIFICADOS
CREATE TABLE clasificados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    equipo_id INT,
    ronda VARCHAR(20)
);