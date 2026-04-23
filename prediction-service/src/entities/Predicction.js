// entities/Prediccion.js
class Prediccion {
    constructor(usuario_id, partido_id, goles_local, goles_visitante) {
        this.usuario_id = usuario_id;
        this.partido_id = partido_id;
        this.goles_local = goles_local;
        this.goles_visitante = goles_visitante;
    }
}
module.exports = Prediccion;