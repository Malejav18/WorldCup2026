// services/PuntajeService.js
const PrediccionRepository = require('../repositories/PrediccionRepository');
const ResultadoRepository  = require('../repositories/ResultadoRepository');
const UsuarioRepository    = require('../repositories/UsuarioRepository');

class PuntajeService {

  /*
   * Reglas de puntuación sugeridas:
   *  - Resultado exacto (marcador):   3 pts
   *  - Solo ganador correcto:         1 pt
   *  - Clasificado de grupo correcto: 2 pts
   *  - Llave correcta por fase:       3 pts (16avos) → 5 (cuartos) → 8 (final)
   */

  async calcularPuntosPartido(usuarioId, resultadoId) {
    const resultado = await ResultadoRepository.findById(resultadoId);
    const preds     = await PrediccionRepository.getPrediccionesPartidoByUsuario(usuarioId);
    const pred      = preds.find(p => p.resultado_id === resultadoId);
    if (!pred || !resultado.goles_local) return 0; // partido no jugado aún

    let puntos = 0;
    if (pred.goles_local === resultado.goles_local &&
        pred.goles_visitante === resultado.goles_visitante) {
      puntos = 3; // marcador exacto
    } else if (pred.ganador === resultado.ganador) {
      puntos = 1; // solo acertó resultado
    }

    await PrediccionRepository.actualizarPuntosPartido(pred.id, puntos);
    return puntos;
  }

  async recalcularTodoElTorneo(usuarioId) {
    const resultados = await ResultadoRepository.findAll();
    let total = 0;
    for (const r of resultados) {
      total += await this.calcularPuntosPartido(usuarioId, r.id);
    }
    // sumar puntos por clasificados y llaves
    total += await this.calcularPuntosClasificados(usuarioId);
    total += await this.calcularPuntosLlaves(usuarioId);
    await UsuarioRepository.actualizarPuntaje(usuarioId, total);
    return total;
  }

  async calcularPuntosClasificados(usuarioId) {
    // Compara PrediccionClasificados del usuario vs ClasificadoFase1 real
    const predichos = await PrediccionRepository.getClasificadosByUsuario(usuarioId);
    const reales    = await require('../repositories/GrupoEquipoRepository').getClasificadosReales();
    let pts = 0;
    for (const p of predichos) {
      if (reales.some(r => r.equipo_id === p.equipo_id && r.grupo_id === p.grupo_id)) pts += 2;
    }
    return pts;
  }

  async calcularPuntosLlaves(usuarioId) {
    // Por cada fase compara si los equipos predichos en la llave coinciden con resultado real
    const PUNTOS_POR_FASE = { '16avos': 3, '8vos': 4, 'cuartos': 5, 'semis': 6, 'final': 8 };
    const predsLlave = await PrediccionRepository.getPrediccionesLlaveByUsuario(usuarioId);
    let pts = 0;
    for (const pred of predsLlave) {
      const real = await require('../repositories/ResultadoRepository').findLlaveReal(pred.fase, pred.equipo1_id, pred.equipo2_id);
      if (real) pts += PUNTOS_POR_FASE[pred.fase] || 3;
    }
    return pts;
  }
}

module.exports = new PuntajeService();