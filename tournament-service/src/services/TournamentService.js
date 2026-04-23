// src/services/TournamentService.js
const repo = require('../repositories/TournamentRepository');

exports.obtenerEquipos = async () => {
    return await repo.getEquipos();
};

exports.obtenerPartidos = async () => {
    return await repo.getPartidos();
};

exports.obtenerPartidosPorFase = async (fase) => {
    return await repo.getPartidosPorFase(fase);
};

exports.registrarResultado = async (id, data) => {

    if (data.goles_local == null || data.goles_visitante == null) {
        throw new Error("Resultado inválido");
    }

    const partido = await repo.getPartidoById(id);

    if (!partido) {
        throw new Error("Partido no existe");
    }

    await repo.updateResultado(id, data.goles_local, data.goles_visitante);

    return { mensaje: "Resultado actualizado" };
};