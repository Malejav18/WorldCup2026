// src/controllers/PrediccionController.js
const service = require('../services/PrediccionService');

exports.crear = async (req, res) => {
    try {
        const result = await service.crearPrediccion(req.body);
        res.json(result);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
};