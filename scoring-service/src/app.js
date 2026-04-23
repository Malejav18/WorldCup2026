// src/app.js
const express = require('express');
const app = express();

const routes = require('./routes');

app.use(express.json());
app.use('/scoring', routes);

app.listen(3004, () => {
    console.log("Scoring Service corriendo en puerto 3004");
});