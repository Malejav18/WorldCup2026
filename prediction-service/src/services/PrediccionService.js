// services/PrediccionService.js
const repo = require('../repositories/PrediccionRepository');

exports.crear = async (data) => {

    if (!data.terceros || data.terceros.length !== 8) {
        throw new Error("Debes seleccionar 8 mejores terceros");
    }

    return await repo.save(data);
};