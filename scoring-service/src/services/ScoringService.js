// src/services/ScoringService.js
const axios = require('axios');
const repo = require('../repositories/ScoringRepository');
const Puntaje = require('../entities/Puntaje');

exports.calcularPuntosUsuario = async (userId) => {

    // 🔗 traer predicciones
    const predRes = await axios.get('http://localhost:3003/predicciones');
    const predicciones = predRes.data;

    // 🔗 traer resultados reales
    const partRes = await axios.get('http://localhost:3002/partidos');
    const partidos = partRes.data;

    let puntos = 0;

    predicciones.forEach(pred => {

        if (pred.usuario_id != userId) return;

        const real = partidos.find(p => p.id == pred.partido_id);

        if (!real || real.goles_local === null) return;

        puntos += repo.calcularPuntosPartido(pred, real);
    });

    return new Puntaje(userId, puntos);
};