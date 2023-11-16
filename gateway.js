const { createProxyMiddleware } = require('http-proxy-middleware');
const socketIO = require('socket.io');
const http = require('http');
const express = require('express');
const CircuitBreaker = require('opossum');

const app = express();
const server = http.createServer(app);
const io = socketIO(server);

const port = 3000;

// Define routes and their corresponding proxies
const routes = [
  { path: '/api/users/register', target: 'http://user_ride_management:5000/api/users/register' },
  { path: '/api/users/login', target: 'http://user_ride_management:5000' },
  { path: '/api/rides/book', target: 'http://user_ride_management:5000' },
  { path: '/api/rides/create', target: 'http://user_ride_management:5000' },
  { path: '/api/rides/available', target: 'http://user_ride_management:5000' },
  { path: '/api/two-phase-commit', target: 'http://user_ride_management:5000/api/two-phase-commit' },
  { path: '/api/chat', target: 'http://realtime_chat:5001', ws: true } // WebSocket proxy
];

// Configure proxies with Circuit Breaker for each route
routes.forEach(({ path, target, ws }) => {
  let circuitBreaker;
  if (ws) {
    // WebSocket proxy
    circuitBreaker = new CircuitBreaker(createWebSocketProxy(target));
  } else {
    // Regular HTTP proxy
    circuitBreaker = new CircuitBreaker(createProxyMiddleware({ target, changeOrigin: true }));
  }

  // Handle Circuit Breaker events
  circuitBreaker.on('open', () => {
    console.log(`Circuit Breaker opened for route: ${path}`);
  });

  circuitBreaker.on('halfOpen', () => {
    console.log(`Circuit Breaker half-opened for route: ${path}`);
  });

  circuitBreaker.on('close', () => {
    console.log(`Circuit Breaker closed for route: ${path}`);
  });

  // Apply the circuit breaker to the route
  app.use(path, (req, res, next) => {
    circuitBreaker.fire(req, res, next);
  });

  // Handle WebSocket connections
  if (ws) {
    io.on('connection', (socket) => {
      // Handle the WebSocket connection as needed
      console.log('Client connected to the WebSocket proxy');
    });
  }
});

server.listen(port, () => {
  console.log(`API Gateway is listening on port ${port}`);
});

// Function to create WebSocket proxy
function createWebSocketProxy(target) {
  return (req, socket, head) => {
    const targetSocket = http.request({
      host: target,
      port: 5000,
      method: req.method,
      headers: req.headers,
    });

    targetSocket.on('upgrade', (targetRes, targetSocket, targetHead) => {
      socket.write('HTTP/1.1 101 Web Socket Protocol Handshake\r\n' +
                   'Upgrade: WebSocket\r\n' +
                   'Connection: Upgrade\r\n' +
                   '\r\n');

      socket.pipe(targetSocket).pipe(socket);
    });

    targetSocket.on('error', (err) => {
      console.error(`WebSocket proxy error: ${err.message}`);
      socket.end();
    });

    socket.on('error', (err) => {
      console.error(`Client socket error: ${err.message}`);
      targetSocket.end();
    });

    targetSocket.end();
  };
}
