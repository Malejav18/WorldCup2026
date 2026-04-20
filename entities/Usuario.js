// entities/Usuario.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Usuario = sequelize.define('usuarios', {
  id:       { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  nombre:   { type: DataTypes.STRING(100) },
  email:    { type: DataTypes.STRING(150), unique: true },
  password: { type: DataTypes.STRING(255) },
  rol:      { type: DataTypes.ENUM('admin', 'jugador') },
  puntaje:  { type: DataTypes.BIGINT, defaultValue: 0 }
});

module.exports = Usuario;