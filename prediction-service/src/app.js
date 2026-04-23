// prediction-service/src/app.js
const express = require('express');
const mysql = require('mysql2/promise');

const app = express();
app.use(express.json());

const db = mysql.createPool({ host:'localhost', user:'root', password:'', database:'mundial' });

app.post('/predicciones', async (req,res)=>{
    const {usuario_id, partido_id, goles_local, goles_visitante, terceros} = req.body;

    if (!terceros || terceros.length !== 8) {
        return res.status(400).send("Debes seleccionar 8 terceros");
    }

    await db.query(
        'INSERT INTO predicciones(usuario_id,partido_id,goles_local,goles_visitante) VALUES (?,?,?,?)',
        [usuario_id,partido_id,goles_local,goles_visitante]
    );

    for (let t of terceros) {
        await db.query('INSERT INTO terceros(usuario_id,equipo_id) VALUES (?,?)',[usuario_id,t]);
    }

    res.send("Predicción guardada");
});

app.get('/predicciones', async (req,res)=>{
    const [rows]=await db.query('SELECT * FROM predicciones');
    res.json(rows);
});

app.listen(3003);