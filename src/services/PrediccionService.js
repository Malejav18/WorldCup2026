// src/services/PrediccionService.js
const repo = require('../repositories/PrediccionRepository');

exports.crearPrediccion = async (data) => {

    // validar terceros
    if (data.terceros.length !== 8) {
        throw new Error("Debes elegir 8 mejores terceros");
    }

    // validar coherencia básica
    if (!data.usuario_id) {
        throw new Error("Usuario requerido");
    }

    return await repo.guardarPrediccion(data);
};