// entities/PrediccionPartido.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const PrediccionPartido = sequelize.define('prediccion_partido', {
  id:             { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  usuario_id:     { type: DataTypes.INTEGER },
  prediccion_llave: { type: DataTypes.INTEGER },      // FK a prediccion_llave (null en fase de grupos)
  goles_local:    { type: DataTypes.INTEGER },
  goles_visitante:{ type: DataTypes.INTEGER },
  puntos:         { type: DataTypes.INTEGER, defaultValue: 0 },
  ganador:        { type: DataTypes.ENUM('local', 'visitante', 'empate') }
});

module.exports = PrediccionPartido;