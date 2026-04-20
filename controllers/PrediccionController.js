// controllers/PrediccionController.js
const PrediccionService  = require('../services/PrediccionService');
const ClasificadoService = require('../services/ClasificadoService');
const LlaveService       = require('../services/LlaveService');
const PuntajeService     = require('../services/PuntajeService');

class PrediccionController {

  // POST /api/predicciones/partido
  async predecirPartido(req, res) {
    try {
      const { resultado_id, goles_local, goles_visitante, ganador } = req.body;
      const usuarioId = req.user.id;
      const pred = await PrediccionService.guardarPrediccionPartido(
        usuarioId, resultado_id, { goles_local, goles_visitante, ganador }
      );
      res.json({ ok: true, data: pred });
    } catch (e) {
      res.status(400).json({ ok: false, message: e.message });
    }
  }

  // POST /api/predicciones/clasificados
  // Body: [{ grupo_id, equipo_id, posicion }, ...]
  async predecirClasificados(req, res) {
    try {
      const resultado = await ClasificadoService.guardarClasificados(
        req.user.id, req.body.seleccion
      );
      res.json({ ok: true, data: resultado });
    } catch (e) {
      res.status(400).json({ ok: false, message: e.message });
    }
  }

  // POST /api/predicciones/llave
  // Body: { fase, equipo1_id, equipo2_id }
  async predecirLlave(req, res) {
    try {
      const { fase, equipo1_id, equipo2_id } = req.body;
      const pred = await LlaveService.guardarPrediccionLlave(
        req.user.id, fase, equipo1_id, equipo2_id
      );
      res.json({ ok: true, data: pred });
    } catch (e) {
      res.status(400).json({ ok: false, message: e.message });
    }
  }

  // GET /api/predicciones/mis-picks
  async getMisPredicciones(req, res) {
    const data = await PrediccionService.getAllByUsuario(req.user.id);
    res.json({ ok: true, data });
  }
}

module.exports = new PrediccionController();