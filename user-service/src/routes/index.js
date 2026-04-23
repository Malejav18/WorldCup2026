// src/routes/index.js
const express = require('express');
const router = express.Router();
const controller = require('../controllers/UsuarioController');

router.post('/', controller.crear);
router.get('/', controller.listar);

module.exports = router;