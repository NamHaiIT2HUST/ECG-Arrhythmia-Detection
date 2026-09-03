const WebSocket = require('ws');

const url = 'ws://localhost:8000/ws/ecg';
console.log('Connecting to', url);
const ws = new WebSocket(url);

ws.on('open', () => {
  console.log('WS open');
});

ws.on('message', (data) => {
  try {
    const obj = JSON.parse(data);
    console.log('MSG:', Object.keys(obj));
  } catch (e) {
    console.log('RAW:', data.toString().slice(0,200));
  }
});

ws.on('close', (code, reason) => console.log('WS closed', code, reason && reason.toString()));
ws.on('error', (err) => console.error('WS error', err && err.message));

ws.on('unexpected-response', (req, res) => {
  console.log('Unexpected response from server:', res.statusCode);
});
