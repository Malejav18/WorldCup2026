// src/controllers/ScoringController.js
const service = require('../services/ScoringService');

exports.getPuntaje = async (req, res) => {
    try {
        const userId = req.params.userId;
        const resultado = await service.calcularPuntosUsuario(userId);
        res.json(resultado);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};