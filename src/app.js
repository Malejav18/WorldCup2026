const express = require('express');
const app = express();
const routes = require('./routes');

app.use(express.json());

app.get('/', (req, res) => {
    res.send('API Mundial 2026 funcionando 🚀');
});

app.use(routes);

app.listen(3000, () => {
    console.log("Servidor corriendo en http://localhost:3000");
});