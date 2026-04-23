// src/repositories/TournamentRepository.js
const db = require('../config/db');

exports.getEquipos = async () => {
    const [rows] = await db.query('SELECT * FROM equipos');
    return rows;
};

exports.getPartidos = async () => {
    const [rows] = await db.query('SELECT * FROM partidos');
    return rows;
};

exports.getPartidoById = async (id) => {
    const [rows] = await db.query('SELECT * FROM partidos WHERE id=?', [id]);
    return rows[0];
};

exports.updateResultado = async (id, goles_local, goles_visitante) => {
    await db.query(
        'UPDATE partidos SET goles_local=?, goles_visitante=? WHERE id=?',
        [goles_local, goles_visitante, id]
    );
};

exports.getPartidosPorFase = async (fase) => {
    const [rows] = await db.query(
        'SELECT * FROM partidos WHERE fase=?',
        [fase]
    );
    return rows;
};