"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    #Count the number of empty cells in the grid
    count = sum(x.count(EMPTY) for x in board)
    
    #if empty count is odd, it's X turn, else it's O turn
    if (count % 2) == 0:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = []

    #if a space is empty, add index to moves array
    for i,j in enumerate(board):
        for m,n in enumerate(j):
            if n == EMPTY:
                moves.append((i,m))
    
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    finalboard = copy.deepcopy(board)
    playerturn = player(board)

    #if cell is empty, insert move onto board
    if finalboard[action[0]][action[1]] == EMPTY:
        finalboard[action[0]][action[1]] = playerturn
    else:
        raise NameError("Not Valid Move")  #move entered is not valid

    return finalboard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    if sum(x.count(EMPTY) for x in board) > 5:
        return None
    
    xwin = [X, X, X]
    owin = [O, O, O]

    for i in range(3):
        verticle = [board[0][i],board[1][i],board[2][i]]
        if board[i][:] == xwin or verticle == xwin:
            return X

        if board[i][:] == owin or verticle == owin:
            return O

    ldiagonal = [board[0][0],board[1][1],board[2][2]]
    rdiagonal = [board[0][2],board[1][1],board[2][0]]

    if ldiagonal == xwin or rdiagonal == xwin:
        return X
    
    if ldiagonal == owin or rdiagonal == owin:
        return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True

    if sum(x.count(EMPTY) for x in board) == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    bestaction = []
    
    if player(board) == X:
        v = -1*float("inf")
        for action in actions(board):
            vold = v
            v = max(v,MinValue(result(board,action)))
            if v != vold:
                bestaction = action
    else:
        v = float("inf")
        for action in actions(board):
            vold = v
            v = min(v,MaxValue(result(board,action)))
            if v != vold:
                bestaction = action
        
    return bestaction


def MaxValue(board):

    if terminal(board):
        return utility(board)

    v = -1*float("inf")
    
    for action in actions(board):
        v = max(v,MinValue(result(board,action)))
        if v == 1:
            return v

    return v

def MinValue(board):

    if terminal(board):
        return utility(board)

    v = float("inf")

    for action in actions(board):
        v = min(v,MaxValue(result(board,action)))
        if v == -1:
            return v

    return v
