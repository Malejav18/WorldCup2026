// src/controllers/UsuarioController.js
const service = require('../services/UsuarioService');

exports.crear = async (req, res) => {
    try {
        const result = await service.crearUsuario(req.body);
        res.json(result);
    } catch (e) {
        res.status(400).json({ error: e.message });
    }
};

exports.listar = async (req, res) => {
    const users = await service.obtenerUsuarios();
    res.json(users);
};