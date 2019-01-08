// express.js uses the builtin http library
// so a http.Server object handles all request at first
// we need to register socket.io with that server
// because it sits on top of http, not on top of express
var express = require('express');
var app = express();
var server = require('http').createServer(app)
var io = require('socket.io').listen(server)
var conf = require('./config.json');

server.listen(conf.port);

// serve files from /public (output dir for webpack!)
app.use(express.static(__dirname + '/public'));

// send /public/index.html for / request
app.get('/', function (req, res) {
	res.sendfile(__dirname + '/public/index.html');
});

// Ajax route: Send number of currently active clients (just the number)
app.get('/numclients', function (req, res) {
	res.send(200, io.engine.clientsCount);
});

// Websocket handling

// someone connects
io.sockets.on('connection', function (socket) {
	socket.emit('chat', { time: new Date(), text: 'Connected to server!' });  // send him a welcome message
	socket.on('chat', function (data) {  // react to future chat messages from that client
		// send the text to all clients
		io.sockets.emit('chat', { time: new Date(), name: data.name || 'anonymous', text: data.text });
	});
	socket.on('disconnect', function () {
		io.sockets.emit('chat', { time: new Date(), name: 'someone', text: 'left the chat' });
	})
});

// tell console that server is up and running
console.log('Server running on http://127.0.0.1:' + conf.port + '/');
