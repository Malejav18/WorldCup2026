// src/app.js
const express = require('express');
const app = express();

const routes = require('./routes');

app.use(express.json());
app.use('/ranking', routes);

app.listen(3005, () => {
    console.log("Ranking Service corriendo en puerto 3005");
});