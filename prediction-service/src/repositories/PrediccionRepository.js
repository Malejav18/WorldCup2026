// repositories/PrediccionRepository.js
const db = require('../config/db');

exports.save = async (data) => {
    const [result] = await db.query(
        'INSERT INTO predicciones(usuario_id, partido_id, goles_local, goles_visitante) VALUES (?,?,?,?)',
        [data.usuario_id, data.partido_id, data.goles_local, data.goles_visitante]
    );
    return result;
};