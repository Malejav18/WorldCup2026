// src/controllers/TournamentController.js
const service = require('../services/TournamentService');

exports.getEquipos = async (req, res) => {
    const equipos = await service.obtenerEquipos();
    res.json(equipos);
};

exports.getPartidos = async (req, res) => {
    const partidos = await service.obtenerPartidos();
    res.json(partidos);
};

exports.getPartidosFase = async (req, res) => {
    const partidos = await service.obtenerPartidosPorFase(req.params.fase);
    res.json(partidos);
};

exports.postResultado = async (req, res) => {
    try {
        const result = await service.registrarResultado(req.params.id, req.body);
        res.json(result);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
};