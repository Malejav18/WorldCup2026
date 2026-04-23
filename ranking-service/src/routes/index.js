// src/routes/index.js
const express = require('express');
const router = express.Router();
const controller = require('../controllers/RankingController');

router.get('/', controller.getRanking);

module.exports = router;