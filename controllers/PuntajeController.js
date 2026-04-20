// controllers/PuntajeController.js
const PuntajeService = require('../services/PuntajeService');
const RankingService = require('../services/RankingService');

class PuntajeController {

  // GET /api/puntaje/ranking
  async getRanking(req, res) {
    const ranking = await RankingService.getRankingGlobal();
    res.json({ ok: true, data: ranking });
  }

  // POST /api/puntaje/recalcular (solo admin)
  async recalcularTodo(req, res) {
    const usuarios = await require('../repositories/UsuarioRepository').findAll();
    for (const u of usuarios) {
      await PuntajeService.recalcularTodoElTorneo(u.id);
    }
    res.json({ ok: true, message: 'Puntajes recalculados' });
  }
}

module.exports = new PuntajeController();