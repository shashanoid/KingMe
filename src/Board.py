# pylint: skip-file
import copy


class Board:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = [None] * 64

        self.player1_count = 12
        self.player2_count = 12

        self.board[1] = Piece(1, player2, False)
        self.board[3] = Piece(3, player2, False)
        self.board[5] = Piece(5, player2, False)
        self.board[7] = Piece(7, player2, False)
        self.board[8] = Piece(8, player2, False)
        self.board[10] = Piece(10, player2, False)
        self.board[12] = Piece(12, player2, False)
        self.board[14] = Piece(14, player2, False)
        self.board[17] = Piece(17, player2, False)
        self.board[19] = Piece(19, player2, False)
        self.board[21] = Piece(21, player2, False)
        self.board[23] = Piece(23, player2, False)

        self.board[40] = Piece(40, player1, False)
        self.board[42] = Piece(42, player1, False)
        self.board[44] = Piece(44, player1, False)
        self.board[46] = Piece(46, player1, False)
        self.board[49] = Piece(49, player1, False)
        self.board[51] = Piece(51, player1, False)
        self.board[53] = Piece(51, player1, False)
        self.board[55] = Piece(51, player1, False)
        self.board[56] = Piece(56, player1, False)
        self.board[58] = Piece(56, player1, False)
        self.board[60] = Piece(60, player1, False)
        self.board[62] = Piece(62, player1, False)

        # Board return results. All CONST.
        self.NO_MOVE_EXISTS = -1
        self.MOVE_FAILED_ILLEGAL = -1
        self.MOVE_NO_JUMP = 0
        self.MOVE_JUMP = 1

    def toJSON(self):
        '''
            toJSON - returns an array of all of the board pieces.
                This array can easily be incorporated into a JSON schema result.
        '''
        result = []
        board = self.board
        for i in range(0, 64):
            if board[i] is None:
                result.append("BLANK")
            elif self.player(i) == self.player1:
                if self.king(i):
                    result.append("P1_KING")
                else:
                    result.append("P1")
            elif self.player(i) == self.player2:
                if self.king(i):
                    result.append("P2_KING")
                else:
                    result.append("P2")
        return result

    def movablePieces(self, player, prevChainJmp):
        '''
            movablePieces: returns a list of movable pieces on the board.
            Args:
                player: Integer
                piece: Integer from 0-63
            Returns:
                Array of integers, where each integer is from 0-63
        '''
        result = []

        if prevChainJmp is not None:
            if not (self.board[prevChainJmp] is not None and self.player(
                    prevChainJmp) == player):
                raise ValueError("ERROR implementing prevChainJmp")
            return [prevChainJmp]

        for i in range(0, 64):
            if self.board[i] is not None and self.player(i) == player:
                if self.canMove(i, prevChainJmp):
                    result.append(i)

        return result

    def makeMove(self, src, dest, prevChainJmp):
        '''
            makeMove: Moves a piece on the board.
            Args:
                piece: Integer from 0-63
                pos: Integer from 0-63
            Returns one
                self.MOVE_FAILED_ILLEGAL (error)
                self.MOVE_NO_JUMP
                self.MOVE_JUMP
        '''
        if dest not in self.getMoves(src, prevChainJmp):
            return self.MOVE_FAILED_ILLEGAL

        result = self.MOVE_NO_JUMP

        if self.isJump(src, dest):
            otherPosDir = (dest - src) // 2
            if otherPosDir not in [9, -9, 7, -7]:
                raise ValueError("Whoops! Bad jump " + str(otherPosDir) + "!")

            if self.board[src + otherPosDir].player == self.player1:
                self.player1_count -= 1
            else:
                self.player2_count -= 1

            self.board[src + otherPosDir] = None

            result = self.MOVE_JUMP

        # Regular move
        self.board[dest] = copy.deepcopy(self.board[src])
        self.board[dest].pos = dest
        self.board[src] = None

        if self.shouldKing(dest):
            self.board[dest].king = True

        return result

    def isJump(self, src, dest):
        return dest in [src + 18, src - 18, src + 14, src - 14]

    def shouldKing(self, pos):
        return ((self.player(pos) == self.player1 and
                 self.row(pos) == 0) or
                (self.player(pos) == self.player2 and
                 self.row(pos) == 7))

    def canMove(self, pos, prevChainJmp):
        return (len(self.getMoves(pos, prevChainJmp)) > 0)

    # conditions - player is an integer for comparison
    def getMoves(self, pos, prevChainJmp):
        if self.board[pos] is None:
            return []
        return [p for p in [self.tryMoveUpLeft(pos, prevChainJmp),
                            self.tryMoveUpRight(pos, prevChainJmp),
                            self.tryMoveDownLeft(pos, prevChainJmp),
                            self.tryMoveDownRight(pos, prevChainJmp)]
                if p != self.NO_MOVE_EXISTS]

    def tryMoveDownLeft(self, pos, prevChainJmp):
        if ((self.player(pos) == self.player2 or self.king(pos)) and
                self.onBoard(pos + 7) and
                self.column(pos) > 0):

            other = self.board[pos + 7]

            if other is None:
                if prevChainJmp is None:
                    return pos + 7

            elif (self.player(pos) != other.player and
                    self.onBoard(pos + 14) and
                    self.column(pos) > 1 and
                    self.board[pos + 14] is None):
                return pos + 14

        # All other test cases fail
        return self.NO_MOVE_EXISTS

    def tryMoveDownRight(self, pos, prevChainJmp):
        if ((self.player(pos) == self.player2 or self.king(pos)) and
                self.onBoard(pos + 9) and
                self.column(pos) < 7):
            other = self.board[pos + 9]
            #Try and move
            if other is None:
                if prevChainJmp is None:
                    return pos + 9

            elif (self.player(pos) != other.player and
                    self.onBoard(pos + 18) and
                    self.column(pos) < 6 and
                    self.board[pos + 18] is None):
                return pos + 18

        return self.NO_MOVE_EXISTS

    def tryMoveUpLeft(self, pos, prevChainJmp):
        if ((self.player(pos) == self.player1 or self.king(pos)) and
                self.onBoard(pos - 9) and
                self.column(pos) > 0):
            # See if the piece is occupied
            other = self.board[pos - 9]
            if other is None:
                if prevChainJmp is None:
                    return pos - 9

            # If so, attempt a jump
            elif (self.player(pos) != other.player and
                    self.onBoard(pos - 18) and
                    self.column(pos) > 1 and
                    self.board[pos - 18] is None):
                return pos - 18

        # All cases fail
        return self.NO_MOVE_EXISTS

    def tryMoveUpRight(self, pos, prevChainJmp):
        if ((self.player(pos) == self.player1 or self.king(pos)) and
                self.onBoard(pos - 7) and
                self.column(pos) < 7):
            other = self.board[pos - 7]
            if other is None:
                if prevChainJmp is None:
                    return pos - 7
            elif (self.player(pos) != other.player and
                  self.onBoard(pos - 14) and
                  self.column(pos) < 6 and
                  self.board[pos - 14] is None):
                return pos - 14

        # All cases fail
        return self.NO_MOVE_EXISTS

    def onBoard(self, pos):
        ''' onBoard - helper function that determines whether a position is
                valid for the board.
            Args:
                pos - Integer
            Returns:
                boolean result
        '''
        return (pos > 0) and (pos <= 63)

    def king(self, pos):
        return self.board[pos].king

    def player(self, pos):
        return self.board[pos].player

    def column(self, pos):
        ''' column - helper function that determines the column of a piece
            Args:
                pos - Integer
            Returns:
                column - Integer
        '''
        return pos % 8

    def row(self, pos):
        ''' onBoard - helper function that determines the row of a piece
            Args:
                pos - Integer
            Returns:
                row - Integer
        '''
        return pos // 8


class Piece:
    def __init__(self, pos, player, king):
        self.pos = pos
        self.player = player
        self.king = king
