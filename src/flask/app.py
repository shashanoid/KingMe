""" app.py
    Contains the logic behind connecting the client and the server
"""
import os
import sys
from flask_socketio import SocketIO, emit, join_room
from flask import Flask, render_template
sys.path.insert(0, 'src/')

try:
    from State import State
except ImportError:
    print('Failed to import Board.py')
    sys.exit()


class Handler:
    """ Class for the flask app object """
    template_dir = os.path.abspath('./src/templates/')
    static_dir = os.path.abspath('./src/static/')
    app = Flask(__name__, template_folder=template_dir,
                static_url_path="", static_folder=static_dir)
    socketio = SocketIO(app)

    def __init__(self):
        """ Initialize handler by initializing room tracking data structure"""
        self.game_handler = UniqueIDGenerator()
        self.player_handler = UniqueIDGenerator()
        self.rooms = {}

    # pylint: disable=R0201
    def index(self):
        """ Returns the index page"""
        return render_template('index.html')

    def create(self):
        """ Create a game lobby """
        # Generate Player ID
        player1_id = self.player_handler.generate_id()

        # Initialize game
        game = State(player1_id)

        # Generate room ID
        room_id = self.game_handler.generate_id()

        # Assign item in dictionary
        self.rooms[room_id] = game

        # Assign session id to room_id (in our case, unique integer identified)
        # Documentation: https://flask-socketio.readthedocs.io/en/latest/
        join_room(room_id)

        # Let client know what player_id and room_id ID were assigned
        self.emit_player_info(player1_id, room_id)
        self.update(room_id)

    def join(self, data):
        """ Join a game lobby and update participants """
        try:
            room_id = int(data['room_id'])
        except ValueError:
            emit('error', {'error': 'Room IDs must be integers'})
            return

        if room_id not in self.rooms:
            emit('error', {'error': 'Room does not exist'})
            return

        # Generate player ID
        player2_id = self.player_handler.generate_id()

        # Add player and then rebroadcast game object
        self.rooms[room_id].join(player2_id)

        # Assign user to session
        join_room(room_id)

        # Let client know what player_id and room_id ID were assigned
        self.emit_player_info(player2_id, room_id)
        self.update(room_id)

    def emit_player_info(self, player_id, room_id):
        """ Informs players of assigned information on joining a room """
        emit('join_room', {'player_id': player_id, 'room_id': room_id})

    def disconnect(self, data):
        """" Defines behavior for when a user disconnects from a room """
        # room_id = data['room_id']
        # player_id = data['player_id']

        # Assign the room with id room_id as inactive
        # and mark player_id player as disconnected
        # pass

    def update(self, room_id):
        """ Broadcasts a game state to players in a room
            You'll want to update the board before calling this function
            """
        emit("update", self.rooms[room_id].toJSON(), room=room_id)

    # pylint: disable=W0613
    def get_moves(self, data):
        """ Get valid moves for a board state """
        piece = int(data['pieceToMove'])
        room_id = data['room_id']
        moves = self.rooms[room_id].getMoves(piece)
        get_moves = {
            'player_id': data['player_id'],
            'pieces': moves,
            'pieceBeingMoved': data['pieceToMove']
        }

        emit("sendMoves", get_moves)

    def make_move(self, data):
        """ This is to handle make move functionality -- [make move schema] """
        if not bool(data['makeMove']):
            if self.rooms[data['room_id']].prevChainJmp is not None:
                self.rooms[data['room_id']].cancelMove()
        else:
            self.rooms[data['room_id']].makeMove(
                int(data['pieceToMove']),
                int(data['moveToLocation'])
            )
        self.update(data['room_id'])
        # Perform computation and update the board with new data


class UniqueIDGenerator:
    """ Class to handle IDs """

    def __init__(self):
        self.uid = 0

    def generate_id(self):
        """ Generates a unique id for a given object """
        self.update_ids()
        return self.uid

    def update_ids(self):
        """ Updates the IDs. This implementation
        increments the ids sequentially """
        self.uid += 1


def get_handler():
    """ Initializes the handlers and adds mapping between endpoints and functions """
    handler = Handler()

    # URL Routes
    handler.app.add_url_rule('/', 'index', handler.index)

    # Socket IO event handling
    handler.socketio.on_event('create', handler.create)
    handler.socketio.on_event('join', handler.join)
    handler.socketio.on_event('exit', handler.disconnect)
    handler.socketio.on_event('getMoves', handler.get_moves)
    handler.socketio.on_event('makeMove', handler.make_move)

    return handler


if __name__ == '__main__':
    HANDLER = get_handler()
    # App configs
    HANDLER.socketio.run(HANDLER.app, host='0.0.0.0', port=5000, debug=True)
