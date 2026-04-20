// repositories/PrediccionRepository.js
const PrediccionPartido    = require('../entities/PrediccionPartido');
const PrediccionLlave      = require('../entities/PrediccionLlave');
const PrediccionClasificados = require('../entities/PrediccionClasificados');

class PrediccionRepository {

  // Fase de grupos: guarda o actualiza el marcador predicho para un partido
  async upsertPrediccionPartido(usuarioId, resultadoId, datos) {
    const [pred] = await PrediccionPartido.upsert({
      usuario_id:      usuarioId,
      resultado_id:    resultadoId,
      goles_local:     datos.goles_local,
      goles_visitante: datos.goles_visitante,
      ganador:         datos.ganador
    });
    return pred;
  }

  // Fase eliminatoria: guarda qué equipo pasa según el usuario en cada llave
  async upsertPrediccionLlave(usuarioId, fase, equipo1Id, equipo2Id) {
    const [pred] = await PrediccionLlave.upsert({
      usuario_id: usuarioId,
      fase,
      equipo1_id: equipo1Id,
      equipo2_id: equipo2Id
    });
    return pred;
  }

  // Predicción de clasificados a 16avos (incluyendo terceros)
  async guardarClasificados(usuarioId, clasificados) {
    // clasificados = [{ grupo_id, equipo_id }, ...]
    await PrediccionClasificados.destroy({ where: { usuario_id: usuarioId } });
    return PrediccionClasificados.bulkCreate(
      clasificados.map(c => ({ usuario_id: usuarioId, ...c }))
    );
  }

  async getPrediccionesPartidoByUsuario(usuarioId) {
    return PrediccionPartido.findAll({ where: { usuario_id: usuarioId } });
  }

  async getPrediccionesLlaveByUsuario(usuarioId) {
    return PrediccionLlave.findAll({ where: { usuario_id: usuarioId } });
  }
}

module.exports = new PrediccionRepository();