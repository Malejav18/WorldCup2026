// src/entities/Usuario.js
class Usuario {
    constructor(id, nombre, email, puntos = 0) {
        this.id = id;
        this.nombre = nombre;
        this.email = email;
        this.puntos = puntos;
    }
}

module.exports = Usuario;