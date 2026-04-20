// entities/PrediccionLlave.js
// Cubre las fases eliminatorias (16avos, 8vos, cuartos, semis, final)
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const PrediccionLlave = sequelize.define('prediccion_llave', {
  id:         { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  usuario_id: { type: DataTypes.INTEGER },
  fase:       { type: DataTypes.ENUM('16avos','8vos','cuartos','semis','final') },
  equipo1_id: { type: DataTypes.INTEGER },   // equipo que el usuario predijo que pasa
  equipo2_id: { type: DataTypes.INTEGER }
});

module.exports = PrediccionLlave;