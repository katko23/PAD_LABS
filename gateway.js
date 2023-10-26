const express = require('express');
const httpProxy = require('http-proxy-middleware');
const socketIO = require('socket.io');
const http = require('http');

const app = express();
const server = http.createServer(app);
const io = socketIO(server);

const port = 3000;

// Define routes and their corresponding proxies
const routes = [
  { path: '/api/users/register', target: 'http://user-ride-management:5000' },
  { path: '/api/users/login', target: 'http://user-ride-management:5000' },
  { path: '/api/rides/book', target: 'http://user-ride-management:5000' },
  { path: '/api/rides/create', target: 'http://user-ride-management:5000' },
  { path: '/api/rides/available', target: 'http://user-ride-management:5000' },
  { path: '/api/chat', target: 'http://realtime-chat:5001', ws: true }, // WebSocket proxy
];

// Configure proxies for each route
routes.forEach(({ path, target, ws }) => {
  if (ws) {
    // WebSocket proxy
    app.use(path, httpProxy({
      target,
      ws: true,
      changeOrigin: true,
      pathRewrite: {
        ['^' + path]: '',
      },
    }));

    // Handle WebSocket connections
    io.on('connection', (socket) => {
      // Handle the WebSocket connection as needed
      console.log('Client connected to the WebSocket proxy');
    });
  } else {
    // Regular HTTP proxy
    app.use(path, httpProxy({ target, changeOrigin: true }));
  }
});

server.listen(port, () => {
  console.log(`API Gateway is listening on port ${port}`);
});
