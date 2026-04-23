// src/services/RankingService.js
const axios = require('axios');
const repo = require('../repositories/RankingRepository');
const Ranking = require('../entities/Ranking');

exports.obtenerRanking = async () => {

    // 🔗 Obtener usuarios
    const usersRes = await axios.get('http://localhost:3001/users');
    const usuarios = usersRes.data;

    const ranking = [];

    // 🔗 Obtener puntos por usuario
    for (let u of usuarios) {

        try {
            const scoreRes = await axios.get(
                `http://localhost:3004/scoring/${u.id}`
            );

            const puntos = scoreRes.data.puntos;

            ranking.push(
                new Ranking(u.id, u.nombre, puntos)
            );

        } catch (err) {
            ranking.push(
                new Ranking(u.id, u.nombre, 0)
            );
        }
    }

    // ordenar ranking
    return repo.ordenarRanking(ranking);
};