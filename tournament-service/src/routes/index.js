// src/routes/index.js
const express = require('express');
const router = express.Router();
const controller = require('../controllers/TournamentController');

router.get('/equipos', controller.getEquipos);
router.get('/partidos', controller.getPartidos);
router.get('/partidos/fase/:fase', controller.getPartidosFase);
router.post('/partidos/:id/resultado', controller.postResultado);

module.exports = router;