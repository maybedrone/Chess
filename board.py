# chess_board.py
BOARD_SIZE = 8
SQUARE_SIZE = 80
LIGHT_COLOR = '#6586A7'
DARK_COLOR = '#EBEBEB'
HIGHLIGHT_COLOR = '#FF8C00'

def initial_board():
    board = []
    for i in range(8):
        row = []
        for j in range(8):
            row.append(None)
        board.append(row)
    # Black pieces
    board[0] = ['r','n','b','q','k','b','n','r']
    board[1] = ['p','p','p','p','p','p','p','p']
    # White pieces
    board[6] = ['P','P','P','P','P','P','P','P']
    board[7] = ['R','N','B','Q','K','B','N','R']
    return board

def inside(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def is_white(piece):
    return piece is not None and piece.isupper()

def is_black(piece):
    return piece is not None and piece.islower()
