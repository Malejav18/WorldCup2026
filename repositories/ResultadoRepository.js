// repositories/ResultadoRepository.js
const Resultado = require('../entities/Resultado');

class ResultadoRepository {
  async findAll()            { return Resultado.findAll({ include: ['equipoLocal','equipoVisitante'] }); }
  async findById(id)         { return Resultado.findByPk(id); }
  async findByGrupo(grupoId) { return Resultado.findAll({ where: { grupo_id: grupoId } }); }
  async create(datos)        { return Resultado.create(datos); }
  async update(id, datos)    { return Resultado.update(datos, { where: { id } }); }
}

module.exports = new ResultadoRepository();