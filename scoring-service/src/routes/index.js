// src/routes/index.js
const express = require('express');
const router = express.Router();
const controller = require('../controllers/ScoringController');

router.get('/:userId', controller.getPuntaje);

module.exports = router;