/** board.js
  * File to handle board manipulations
  *
  **/


//global variable to save the board state


var saveCurrentState = null;
var previousCells = [];

$(document).ready(function () {
    // Make sure the enter key works on our input field
    var input = document.getElementById("joinInput");
    input.addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            $('#joinGame').click();
        }
    });
});

function setupGamePage() {
    $(".menu").hide();
    $("h5").show();
    $("#gameBoard").show();
}

// createGame onclick - emit a message on the 'create' channel to
// create a new game with default parameters
function createGame() {
    socket.emit('create');
}

// Join existing game
function joinGame(roomID) {
    socket.emit('join', {
        'room_id': $('#joinInput').val()
    });
}

function genBoard(data) {
    //function to generate gameBoard with clickable cells
    //based on given board state
    saveCurrentState = data;
    previousCells = [];

    var header = $('#user_message_header');

    if (["P1_WIN", "P2_WIN", "P1_DISCONNECT", "P2_DISCONNECT"].includes(data.state)) {
        gameEndDisplay(header, data.state);
        return;
    }
    //generate board
    board = data.board;
    for (var i = 0; i < board.length; i++) {
        var cell_state = board[i];
        setCell(i, cell_state);
    }
    if (data.state == "WAITING") {
        setHeaderMessage("Waiting for other player to connect... Room: " + room_id);
        return;
    }

    highlightBoard(data);
}


function highlightBoard(data) {
    /**
    * Highlights the board if it is the current active player's turn
    * @param {*} data
    */
    // if it is NOT the player's turn, don't highlight anything
    if (data.playerTurn != player_id) {
        setHeaderMessage("Waiting on other player's turn to end...");
        return;
    }

    setHeaderMessage("It is your turn.");

    movablePieces = data.movablePieces;

    for (var j = 0; j < movablePieces.length; j++) {
        var index = movablePieces[j];
        setHighlight(index, data.state);
    }
    isSecondMove = data.secondMove;

    if (isSecondMove == true) {
        setHeaderMessage("You can either make another move or dismiss by clicking on itself.");
    }
}

function setHeaderMessage(message) {
    var header = $('#user_message_header');
    header.text(message);
    header.show();
}

function gameEndDisplay(header, state) {
    if (state == "P1_WIN")
        header.text("Game Ends: Player 1 Wins!");
    else if (state == "P2_WIN")
        header.text("Game Ends: Player 2 Wins!");
    else if (state == "P1_DISCONNECT")
        header.text("Game Ends: Player 1 disconnected, Player 2 Wins by Forfeit");
    else if (state == "P2_DISCONNECT")
        header.text("Game Ends: Player 2 disconnected, Player 1 Wins by Forfeit");
    header.show();
    $("#gameBoard").hide();
}

function setCell(index, state) {
    var cell = $("#game_cell_" + index);
    cell.empty();
    cell.removeClass("highlighted");
    if (state == "BLANK") {
        return;
    }
    cell.append(createPiece(state));
}

function setHighlight(index, state) {
    var cell = $("#game_cell_" + index);
    cell.addClass('highlighted');
}

function createPiece(player) {
    var $div = $("<div>", { "class": "checker" });
    $div.addClass(player);
    return $div;
}

// Function to call to server an action
function clickGameCell(cell) {
    var cell_num = cell.id.match(/\d/g);
    cell_num = cell_num.join("");
    previousCells.push(cell_num);

    if(previousCells[previousCells.length -1] != cell_num){
        previousCells.push(cell_num);
    }

    // If the cell is not highlighted, do nothing.
    if (!$(cell).hasClass('highlighted')) {
        return;
    }

    // If the cell does not contain a piece, make the move
    if (!cell.innerHTML) {
        makeMove(cell_num);
        return;
    }

    // If we clicked on the last piece, regenerate the board using saved state
    if (cell_num == previousCell()) {
        if (saveCurrentState.secondMove) {
            // Make no move
            makeNoMove();
            return;
        }

        // Reset board
        resetBoard();
        return;
    }

    // Finally, if the piece clicked
    getMoves(cell_num);
}

function resetBoard() {
    // Resets the board to the last known state
    genBoard(saveCurrentState);
}

function previousCell() {
    /**
     * Returns the position of the last cell that was clicked
     */
    return previousCells[previousCells.length - 2];
}

function getMoves(cell_num) {
    movablePieces = saveCurrentState.movablePieces;

    for (var i = 0; i < movablePieces.length; i++) {
        var highlightedID = document.getElementById("game_cell_" + movablePieces[i]);

        if (movablePieces[i] != cell_num) {
            highlightedID.classList.remove("highlighted");
        }
    }

    //sends the data via post and perform 'function' if successful
    socket.emit('getMoves', {
        'player_id': saveCurrentState.playerTurn,
        'pieceToMove': cell_num,
        'room_id': room_id
    });
}

// Send make move schema
function makeMove(cell_num) {
    socket.emit('makeMove', {
        'player_id': saveCurrentState.playerTurn,
        'pieceToMove': previousCells[previousCells.length - 2],
        'moveToLocation': cell_num,
        'room_id': room_id,
        'makeMove': true
    });
}

function forceMove(start, end) {
    socket.emit('makeMove', {
        'player_id': saveCurrentState.playerTurn,
        'pieceToMove': start,
        'moveToLocation': end,
        'room_id': room_id,
        'makeMove': true
    });
}

function makeNoMove() {
    // On second turn, and don't want to double jump
    // send false
    socket.emit('makeMove', {
        'makeMove': false,
        'room_id': room_id
    });
}


// Highlights the send moves received from server
function highlightSendMoves(data) {
    toHighlight = data.pieces;
    player_id = data.player_id;

    if (player_id == saveCurrentState.playerTurn) {
        for (var i = 0; i < toHighlight.length; i++) {
            setHighlight(toHighlight[i], saveCurrentState);
        }
    }

}