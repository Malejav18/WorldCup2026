// src/repositories/RankingRepository.js

exports.ordenarRanking = (lista) => {
    return lista.sort((a, b) => b.puntos - a.puntos);
};