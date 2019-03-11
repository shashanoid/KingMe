""" Test Module
    Contains test cases for the entire application
    E0401 is disabled because locally pylint has no issues importing app
    after the path insert, however pylint is having some difficulties on the gitlab runners

    C0413 is disabled because we require the sys.path.insert before importing
"""
import sys
import unittest
sys.path.insert(0, 'src/flask')
sys.path.insert(0, 'src/')

try:
    from app import get_handler
    from State import State
except ImportError:
    print("Failed to import")
    sys.exit(1)


class TestSocketIo(unittest.TestCase):
    """ Flask Test Class
        Each member function is a test case
    """
    @classmethod
    def setUpClass(cls):
        """ Set up the class by defining handler, app, and socketio """
        cls.HANDLER = get_handler()
        cls.APP = cls.HANDLER.app
        cls.socketio = cls.HANDLER.socketio

    def test_index(self):
        """ Ensure that Flask was setup correctly"""
        tester = self.APP.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def create_test_client(self):
        """ Create a test client for the socketio application """
        return self.socketio.test_client(self.APP)

    def test_connect(self):
        """ Test connection """
        client = self.create_test_client()
        self.assertTrue(client.is_connected())

        # Confirm that nothing is sent on connection
        received = client.get_received()
        self.assertEqual(len(received), 0)

    def test_create(self):
        """ Functionality for creating a room """
        client = self.create_test_client()
        client.emit('create')
        received = client.get_received()
        self.assertEqual(len(received), 2)

        # Get the first item received (we've only emitted once)
        received = received[0]
        name = received['name']
        args = received['args']

        # Confirm that join_room endpoint is received
        self.assertEqual(name, 'join_room')

        # Confirm args only has 1 item
        self.assertEqual(len(args), 1)

        data = args[0]
        # Confirm player_id is in data
        self.assertTrue('player_id' in data)
        self.assertTrue('room_id' in data)

        # Confirm player id is 1
        self.assertEqual(data['player_id'], 1)
        self.assertEqual(data['room_id'], 1)

    def test_join_non_existent_room(self):
        """ Check to make sure an error is output when
        joining a room that does not exist """
        client = self.create_test_client()
        # Non-existing room
        client.emit('join', {'room_id': 0})
        received = client.get_received()

        # Get the first item
        received = received[0]

        name = received['name']
        args = received['args']

        # Confirm the endpoint is 'error'
        self.assertEqual(name, 'error')

        # Confirm that data contains error
        self.assertEqual(len(args), 1)

        data = args[0]
        self.assertTrue('error' in data)

        self.assertEqual(data['error'], 'Room does not exist')

    def test_join_room_with_bad_id(self):
        """ Check joining a room with an invalid type of room ID """
        client = self.create_test_client()

        # Empty string, random string, and float test cases
        test_case = ['', 'abcd', '1.23']

        for case in test_case:
            client.emit('join', {'room_id': case})

        # Make sure that each case has the proper error message
        for received_item in client.get_received():
            args = received_item['args']
            data = args[0]
            self.assertTrue('error' in data)
            self.assertEqual(data['error'], 'Room IDs must be integers')

    def test_join_created_room(self):
        """ Create a room and then join it with a different client """
        # Create each client
        player1 = self.create_test_client()
        player2 = self.create_test_client()

        # Create the room and get the room_id
        player1.emit('create')
        created_room_id = player1.get_received()[0]['args'][0]['room_id']

        # Join the room with player 2
        player2.emit('join', {'room_id': created_room_id})

        # Extract the data received
        received = player2.get_received()[0]
        data = received['args'][0]

        # Confirm player id is 3 (test_create uses id 1) and room_id is 1
        self.assertTrue('player_id' in data)
        self.assertTrue('room_id' in data)

    def test_make_move(self):
        """ p_1 win by eating all pieces """
        player1 = self.create_test_client()
        player2 = self.create_test_client()

        player1.emit('create')
        room_id = player1.get_received()[0]['args'][0]['room_id']
        player2.emit('join', {'room_id': room_id})
        p_1 = player1
        p_2 = player2
        moves = [
            (40, 33, p_1), (17, 26, p_2), (33, 24,
                                           p_1), (10, 17, p_2), (24, 10, p_1),
            (3, 17, p_2), (44, 37, p_1), (26, 35,
                                          p_2), (46, 39, p_1), (21, 30, p_2),
            (39, 21, p_1), (21, 3, p_1), (1, 10,
                                          p_2), (42, 33, p_1), (19, 28, p_2),
            (37, 19, p_1), (19, 1, p_1), (17, 26, p_2), (1, 10, p_1), (8, 17, p_2),
            (10, 24, p_1), (35, 42, p_2), (49, 35,
                                           p_1), (35, 17, p_1), (23, 30, p_2),
            (55, 46, p_1), (5, 12, p_2), (46, 37,
                                          p_1), (14, 21, p_2), (3, 10, p_1),
            (7, 14, p_2), (37, 23, p_1), (23, 5,
                                          p_1), (p_1, "pass"), (21, 30, p_2),
            (5, 19, p_1), (30, 39, p_2), (19, 28, p_1), (39, 46,
                                                         p_2), (53, 39, p_1)
        ]

        play_game(moves, room_id)

    def test_make_move_2(self):
        """ p_1 win by no moves left for p_2 """
        player1 = self.create_test_client()
        player2 = self.create_test_client()

        player1.emit('create')
        room_id = player1.get_received()[0]['args'][0]['room_id']
        player2.emit('join', {'room_id': room_id})
        p_1 = player1
        p_2 = player2
        moves = [(40, 33, p_1), (17, 26, p_2), (33, 24, p_1), (10, 17, p_2), (24, 10, p_1),
                 (3, 17, p_2), (44, 37, p_1), (26, 35, p_2), (46, 39, p_1), (21, 30, p_2),
                 (39, 21, p_1), (21, 3, p_1), (1, 10, p_2), (42, 33, p_1), (19, 28, p_2),
                 (37, 19, p_1), (19, 1, p_1), (17, 26, p_2), (1, 10, p_1), (8, 17, p_2),
                 (10, 24, p_1), (35, 42, p_2), (49, 35, p_1), (35, 17, p_1), (23, 30, p_2),
                 (55, 46, p_1), (5, 12, p_2), (46, 37, p_1), (14, 21, p_2), (3, 10, p_1),
                 (7, 14, p_2), (37, 23, p_1), (23, 5, p_1), (p_1, "pass"), (21, 30, p_2),
                 (5, 19, p_1), (30, 39, p_2), (19, 28, p_1), (39, 46, p_2), (53, 44, p_1),
                 (46, 55, p_2)]
        play_game(moves, room_id)

    def test_make_move_3(self):
        """ Somehow missed moving bottom-left in the past two test cases """
        player1 = self.create_test_client()
        player2 = self.create_test_client()

        player1.emit('create')
        room_id = player1.get_received()[0]['args'][0]['room_id']
        player2.emit('join', {'room_id': room_id})
        p_1 = player1
        p_2 = player2
        moves = [
            (40, 33, p_1), (17, 26, p_2), (33, 24, p_1), (10, 17, p_2), (24, 10, p_1),
            (3, 17, p_2), (44, 37, p_1), (26, 35, p_2), (46, 39, p_1), (21, 30, p_2),
            (39, 21, p_1), (21, 3, p_1), (23, 30, p_2), (3, 10, p_1), (30, 44, p_2)]
        play_game(moves, room_id)

    def test_get_moves(self):
        """ Tests the 'getMoves' socketio endpoint """
        # Create each client
        player1 = self.create_test_client()
        player2 = self.create_test_client()

        player1.emit('create')
        data = player1.get_received()[0]['args'][0]
        room_id = data['room_id']
        player1_id = data['player_id']
        player2.emit('join', {'room_id': room_id})

        player1.emit('getMoves', {
            'pieceToMove': 40,
            'room_id': room_id,
            'player_id': player1_id
        })

        data = player1.get_received()[-1]['args'][0]
        self.assertEqual(data['pieces'], [33])
        self.assertEqual(data['pieceBeingMoved'], 40)


def play_game(moves, room_id):
    """ Simulate a game by executing a set of moves """
    for move in moves:
        make_move(move, room_id)


def make_move(data, room_id):
    """ Make a move or make no move
        ARGS:
            data: tuple
                data[0]: source (Int)
                data[1]: dest   (Int)
                data[2]: client (test_client)
            OR
            data: tuple
                data[0]: client
                data[1]: "pass"
    """
    if data[1] == "pass":
        data[0].emit('makeMove', {
            'makeMove': False,
            'room_id': room_id
        })
        return
    data[2].emit('makeMove', {
        'makeMove': True,
        'room_id': room_id,
        'pieceToMove': data[0],
        'moveToLocation': data[1]
    })


class TestBoard(unittest.TestCase):
    """ End states are quite cumbersome to reach so we can force each method
        just to make sure nothing crashes """

    def setUp(self):
        """ setup """
        self.player1 = 0
        self.player2 = 1

    def test_end_state(self):
        """ Force the state.end function call """
        state = State(self.player1)
        state.join(self.player2)
        state.end("force end")


if __name__ == "__main__":
    unittest.main()
