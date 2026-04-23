// gateway/app.js
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

app.use('/users', createProxyMiddleware({ target: 'http://localhost:3001', changeOrigin: true }));
app.use('/tournament', createProxyMiddleware({ target: 'http://localhost:3002', changeOrigin: true }));
app.use('/predictions', createProxyMiddleware({ target: 'http://localhost:3003', changeOrigin: true }));
app.use('/scoring', createProxyMiddleware({ target: 'http://localhost:3004', changeOrigin: true }));
app.use('/ranking', createProxyMiddleware({ target: 'http://localhost:3005', changeOrigin: true }));

app.listen(3000, () => console.log("Gateway corriendo en 3000"));