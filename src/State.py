# pylint: skip-file
from Board import Board, Piece
'''
    Possible states:
        P1_TURN, P2_TURN, WAITING, P1_WIN, P2_WIN,
        P1_DISCONNECT, P2_DISCONNECT
'''

# abstracting representation of state and players
P1_TURN = "P1_TURN"
P2_TURN = "P2_TURN"
WAITING = "WAITING"
P1_WIN = "P1_WIN"
P2_WIN = "P2_WIN"
P1_DISCONNECT = "P1_DISCONNECT"
P2_DISCONNECT = "P2_DISCONNECT"


class State:
    def __init__(self, player1):
        self.player1 = player1
        self.player2 = None
        self.board = Board(self.player1, -1)
        self.state = "WAITING"
        self.done = False
        self.playerTurn = player1
        self.prevChainJmp = None

    def changeTurn(self):
        if self.playerTurn == self.player1:
            self.playerTurn = self.player2
        else:
            self.playerTurn = self.player1

    def cancelMove(self):
        self.changeTurn()
        self.prevChainJmp = None

    def makeMove(self, src, dest):
        '''
        makeMove - attempts to make a move on the board.

        Args:
            piece: integer
            pos: integer

        Returns:
            One of (int):
                -1 - Board move failed (Board.MOVE_FAILED_ILLEGAL)
                0  - Board move succeeded, no jump (Board.MOVE_NO_JUMP)
                1  - Board move succeeded, jump (Board.MOVE_JUMP)
        '''
        result = self.board.makeMove(src, dest, self.prevChainJmp)
        if result == self.board.MOVE_FAILED_ILLEGAL:
            raise ValueError("ERROR: Illegal move attempted!")

        if self.board.player1_count == 0:
            self.state = P2_WIN
            return result
        if self.board.player2_count == 0:
            self.state = P1_WIN
            return result

        # If no jump happened or the player cannot make a second jump
        if result != self.board.MOVE_JUMP or len(
                self.board.getMoves(dest, True)) == 0:
            self.changeTurn()
            self.prevChainJmp = None
        else:
            self.prevChainJmp = dest
        return result

    def getMoves(self, pos):
        return self.board.getMoves(pos, self.prevChainJmp)

    def toJSON(self):
        return {
            'playerTurn': self.playerTurn,
            'secondMove': self.prevChainJmp,
            'players': [self.player1, self.player2],
            'board': self.board.toJSON(),
            'movablePieces': self.getMovablePieces(),
            'state': self.state,
        }

    def getMovablePieces(self):
        if self.state not in [P1_TURN, P2_TURN]:
            return []
        result = self.board.movablePieces(self.playerTurn, self.prevChainJmp)
        if len(result) == 0:
            if self.playerTurn == self.player1:
                self.state = P2_WIN
            else:
                self.state = P1_WIN

        return result

    def join(self, player2):
        self.player2 = player2
        self.board = Board(self.player1, self.player2)
        self.state = P1_TURN

    def end(self, reason):
        self.done = True
        self.state = reason
