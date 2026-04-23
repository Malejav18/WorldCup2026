// user-service/src/app.js
const express = require('express');
const mysql = require('mysql2/promise');

const app = express();
app.use(express.json());

const db = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'mundial'
});

app.post('/users', async (req, res) => {
    const { nombre, email } = req.body;
    const [r] = await db.query(
        'INSERT INTO usuarios(nombre,email) VALUES (?,?)',
        [nombre, email]
    );
    res.json({ id: r.insertId, nombre, email });
});

app.get('/users', async (req, res) => {
    const [rows] = await db.query('SELECT * FROM usuarios');
    res.json(rows);
});

app.listen(3001, () => {
    console.log("✅ User Service corriendo en puerto 3001");
});