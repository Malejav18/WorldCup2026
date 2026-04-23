// controllers/PrediccionController.js
const service = require('../services/PrediccionService');

exports.crear = async (req, res) => {
    try {
        const r = await service.crear(req.body);
        res.json(r);
    } catch (e) {
        res.status(400).json({ error: e.message });
    }
};