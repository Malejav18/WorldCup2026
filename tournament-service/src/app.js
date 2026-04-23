// src/app.js
const express = require('express');
const app = express();

const routes = require('./routes');

app.use(express.json());
app.use('/', routes);

app.listen(3002, () => {
    console.log("Tournament Service corriendo en puerto 3002");
});