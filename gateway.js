const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const port = 3000;

// Define routes and their corresponding proxies
const routes = [
  { path: '/api/users/register', target: 'http://127.0.0.1:5000' },
  { path: '/api/users/login', target: 'http://127.0.0.1:5000' },
  { path: '/api/rides/book', target: 'http://127.0.0.1:5000' },
  { path: '/api/rides/create', target: 'http://127.0.0.1:5000' },
  { path: '/api/rides/available', target: 'http://127.0.0.1:5000' },
  { path: '/ride', target: 'http://127.0.0.1:5001' },
];

// Configure proxies for each route
routes.forEach(({ path, target }) => {
  app.use(path, createProxyMiddleware({ target, changeOrigin: true }));
});

app.listen(port, () => {
  console.log(`API Gateway is listening on port ${port}`);
});