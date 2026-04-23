// src/entities/Partido.js
class Partido {
    constructor(id, equipo_local, equipo_visitante, goles_local, goles_visitante, fase) {
        this.id = id;
        this.equipo_local = equipo_local;
        this.equipo_visitante = equipo_visitante;
        this.goles_local = goles_local;
        this.goles_visitante = goles_visitante;
        this.fase = fase;
    }
}

module.exports = Partido;