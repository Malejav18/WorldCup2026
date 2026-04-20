// routes/index.js
const express  = require('express');
const router   = express.Router();
const authMw   = require('../middlewares/auth.middleware');

const AuthCtrl        = require('../controllers/AuthController');
const PrediccionCtrl  = require('../controllers/PrediccionController');
const PuntajeCtrl     = require('../controllers/PuntajeController');
const PartidoCtrl     = require('../controllers/PartidoController');
const GrupoCtrl       = require('../controllers/GrupoController');

// Públicas
router.post('/auth/registro', AuthCtrl.registro);
router.post('/auth/login',    AuthCtrl.login);

// Protegidas
router.use(authMw);
router.get ('/grupos',                         GrupoCtrl.getGrupos);
router.post('/predicciones/partido',           PrediccionCtrl.predecirPartido);
router.post('/predicciones/clasificados',      PrediccionCtrl.predecirClasificados);
router.post('/predicciones/llave',             PrediccionCtrl.predecirLlave);
router.get ('/predicciones/mis-picks',         PrediccionCtrl.getMisPredicciones);
router.get ('/puntaje/ranking',                PuntajeCtrl.getRanking);

// Solo admin
router.post('/admin/resultado',                PartidoCtrl.cargarResultado);
router.post('/admin/puntaje/recalcular',       PuntajeCtrl.recalcularTodo);

module.exports = router;