// src/repositories/PrediccionRepository.js
const db = require('../config/db');

exports.guardarPrediccion = async (data) => {
    const [result] = await db.query(
        'INSERT INTO predicciones SET ?', data
    );
    return result;
};