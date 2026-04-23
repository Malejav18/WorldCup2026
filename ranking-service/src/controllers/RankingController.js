// src/controllers/RankingController.js
const service = require('../services/RankingService');

exports.getRanking = async (req, res) => {
    try {
        const ranking = await service.obtenerRanking();
        res.json(ranking);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};