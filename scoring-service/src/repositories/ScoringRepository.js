// src/repositories/ScoringRepository.js

exports.calcularPuntosPartido = (pred, real) => {

    // marcador exacto
    if (pred.goles_local == real.goles_local &&
        pred.goles_visitante == real.goles_visitante) {
        return 3;
    }

    // solo resultado (ganador/empate)
    const resultadoPred =
        pred.goles_local > pred.goles_visitante ? 'L' :
        pred.goles_local < pred.goles_visitante ? 'V' : 'E';

    const resultadoReal =
        real.goles_local > real.goles_visitante ? 'L' :
        real.goles_local < real.goles_visitante ? 'V' : 'E';

    if (resultadoPred === resultadoReal) {
        return 1;
    }

    return 0;
};