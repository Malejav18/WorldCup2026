# WorldCup2026


src/
├── controllers/

│   ├── AuthController.js

│   ├── PartidoController.js
│   ├── PrediccionController.js
│   ├── ClasificadoController.js
│   ├── LlaveController.js
│   ├── GrupoController.js
│   ├── PuntajeController.js
│   └── UsuarioController.js
│
├── services/
│   ├── AuthService.js
│   ├── PrediccionService.js
│   ├── PuntajeService.js
│   ├── ClasificadoService.js
│   ├── LlaveService.js
│   ├── GrupoService.js
│   ├── ResultadoService.js
│   └── RankingService.js
│
├── repositories/
│   ├── UsuarioRepository.js
│   ├── PrediccionRepository.js
│   ├── ResultadoRepository.js
│   └── GrupoEquipoRepository.js
│
├── entities/
│   ├── Usuario.js
│   ├── Equipo.js
│   ├── Grupo.js
│   ├── GrupoEquipo.js
│   ├── Resultado.js
│   ├── ClasificadoFase1.js
│   ├── PrediccionPartido.js
│   ├── PrediccionLlave.js
│   └── PrediccionClasificados.js
│
├── routes/
│   └── index.js
├── middlewares/
│   └── auth.middleware.js
└── app.js
