// src/services/UsuarioService.js
const repo = require('../repositories/UsuarioRepository');

exports.crearUsuario = async (data) => {
    if (!data.nombre || !data.email) {
        throw new Error("Datos incompletos");
    }
    return await repo.create(data);
};

exports.obtenerUsuarios = async () => {
    return await repo.findAll();
};