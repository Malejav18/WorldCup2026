function mostrar(seccion) {
    document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
    document.getElementById(seccion).classList.add('active');
}

// GUARDAR PREDICCIÓN
async function guardarPrediccion() {

    const data = {
        usuario_id: document.getElementById('usuario').value,
        partido_id: document.getElementById('partido').value,
        goles_local: document.getElementById('local').value,
        goles_visitante: document.getElementById('visitante').value,
        terceros: [1,2,3,4,5,6,7,8]
    };

    await fetch('http://localhost:3000/predictions/predicciones', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    alert("Predicción guardada ⚽");
}

// VER RANKING
async function cargarRanking() {

    const res = await fetch('http://localhost:3000/ranking/ranking');
    const data = await res.json();

    const contenedor = document.getElementById('tablaRanking');
    contenedor.innerHTML = '';

    data.forEach((u, index) => {
        contenedor.innerHTML += `
            <div class="ranking-item">
                <span>#${index + 1} ${u.nombre}</span>
                <span>${u.puntos} pts</span>
            </div>
        `;
    });
}

// Cargar ranking automáticamente
document.addEventListener("DOMContentLoaded", cargarRanking);