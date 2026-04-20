// services/LlaveService.js
// Al ingresar predicción de una llave, verifica que los equipos elegidos
// coincidan con lo que el usuario predijo en la ronda anterior
class LlaveService {

  ORDEN_FASES = ['16avos', '8vos', 'cuartos', 'semis', 'final'];

  async validarLlave(usuarioId, fase, equipo1Id, equipo2Id) {
    const faseIdx = this.ORDEN_FASES.indexOf(fase);
    if (faseIdx === 0) return true; // 16avos: solo verifica que equipos estén en clasificados

    const faseAnterior   = this.ORDEN_FASES[faseIdx - 1];
    const llaveAnterior  = await require('../repositories/PrediccionRepository')
      .getLlaveFaseByUsuario(usuarioId, faseAnterior);

    const equiposQuePasaron = llaveAnterior.flatMap(l => [l.equipo1_id, l.equipo2_id]);
    if (!equiposQuePasaron.includes(equipo1Id) || !equiposQuePasaron.includes(equipo2Id)) {
      throw new Error(`Los equipos deben coincidir con tus predicciones de ${faseAnterior}`);
    }
    return true;
  }

  async guardarPrediccionLlave(usuarioId, fase, equipo1Id, equipo2Id) {
    await this.validarLlave(usuarioId, fase, equipo1Id, equipo2Id);
    return require('../repositories/PrediccionRepository')
      .upsertPrediccionLlave(usuarioId, fase, equipo1Id, equipo2Id);
  }
}

module.exports = new LlaveService();