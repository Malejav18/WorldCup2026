// src/routes/index.js
const express = require('express');
const router = express.Router();
const PrediccionController = require('../controllers/PrediccionController');

router.post('/predicciones', PrediccionController.crear);

module.exports = router;