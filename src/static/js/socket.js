/**
    File to connect client and server
**/

// Establish connection
var socket = io.connect('http://' + document.domain + ':' + location.port);
var player_id = null;
var room_id = null;

// Assigns global client variables and sets up game page when joining a room
socket.on('join_room', function(msg) {
    player_id = msg.player_id;
    room_id = msg.room_id;
    setupGamePage();
});

// message handler for 'error'
socket.on('error', function(msg) {
    alert(msg.error);
});

// Handler for board updates
// Sets up the board given a board state in data

// Creating a new board on top of the existing one.
socket.on('update', function(data) {
    genBoard(data);
});

socket.on('sendMoves', function(data){
    highlightSendMoves(data);
});

