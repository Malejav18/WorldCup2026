// entities/PrediccionClasificados.js
// El usuario escoge qué 32 equipos avanzan a 16avos (16 primeros + 8 terceros)
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const PrediccionClasificados = sequelize.define('prediccion_clasificados', {
  id:         { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  usuario_id: { type: DataTypes.INTEGER },
  grupo_id:   { type: DataTypes.INTEGER },
  equipo_id:  { type: DataTypes.INTEGER }   // equipo predicho a clasificar de ese grupo
});

module.exports = PrediccionClasificados;