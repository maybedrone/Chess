# chess_game.py
import tkinter as tk
from tkinter import messagebox
from board import *
from pieces import *

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title('Chess Game')
        self.canvas = tk.Canvas(root, width=SQUARE_SIZE*BOARD_SIZE, height=SQUARE_SIZE*BOARD_SIZE)
        self.canvas.pack()

        self.board = initial_board()
        self.turn_white = True
        self.selected = None
        self.highlight_ids = []
        self.piece_text_ids = []
        for i in range(8):
            row = []
            for j in range(8):
                row.append(None)
            self.piece_text_ids.append(row)

        self.draw_board()
        self.canvas.bind('<Button-1>', self.on_click)

        frame = tk.Frame(root)
        frame.pack()
        tk.Button(frame, text='Reset', command=self.reset).pack(side='left')

    def reset(self):
        self.board = initial_board()
        self.turn_white = True
        self.selected = None
        self.redraw()

    def draw_board(self):
        self.canvas.delete('square')
        for r in range(8):
            for c in range(8):
                x1 = c*SQUARE_SIZE
                y1 = r*SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                color = LIGHT_COLOR if (r+c)%2==0 else DARK_COLOR
                self.canvas.create_rectangle(x1,y1,x2,y2, fill=color, outline='', tags='square')
        self.redraw_pieces()

    def redraw(self):
        self.canvas.delete('all')
        self.draw_board()

    def redraw_pieces(self):
        for r in range(8):
            for c in range(8):
                if self.piece_text_ids[r][c] is not None:
                    self.canvas.delete(self.piece_text_ids[r][c])
                    self.piece_text_ids[r][c] = None
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None:
                    glyph = PIECE_GLYPHS[piece]
                    x = c*SQUARE_SIZE + SQUARE_SIZE//2
                    y = r*SQUARE_SIZE + SQUARE_SIZE//2
                    tid = self.canvas.create_text(x,y,text=glyph,font=('Arial',32),tags='piece')
                    self.piece_text_ids[r][c] = tid

    def on_click(self, event):
        c = event.x // SQUARE_SIZE
        r = event.y // SQUARE_SIZE
        if not inside(r,c):
            return
        piece = self.board[r][c]

        if self.selected is None:
            if piece is None:
                return
            if self.turn_white and not is_white(piece):
                return
            if not self.turn_white and not is_black(piece):
                return
            self.selected = (r,c)
            self.highlight_square(r,c)
        else:
            sr, sc = self.selected
            if self.try_move(sr, sc, r, c):
                self.turn_white = not self.turn_white
                if self.is_king_captured():
                    winner = 'White' if self.turn_white == False else 'Black'
                    messagebox.showinfo('Game Over', f'{winner} captured the king!')
                    self.reset()
            self.selected = None
            self.clear_highlights()
            self.redraw_pieces()

    def highlight_square(self, r, c):
        self.clear_highlights()
        x1 = c*SQUARE_SIZE
        y1 = r*SQUARE_SIZE
        x2 = x1 + SQUARE_SIZE
        y2 = y1 + SQUARE_SIZE
        hid = self.canvas.create_rectangle(x1,y1,x2,y2, outline='blue', width=3)
        self.highlight_ids.append(hid)

    def clear_highlights(self):
        for hid in self.highlight_ids:
            self.canvas.delete(hid)
        self.highlight_ids = []

    def try_move(self, sr, sc, tr, tc):
        piece = self.board[sr][sc]
        target = self.board[tr][tc]

        if not self.is_legal_move(sr, sc, tr, tc):
            return False

        self.board[tr][tc] = piece
        self.board[sr][sc] = None
        return True

    def is_legal_move(self, sr, sc, tr, tc):
        piece = self.board[sr][sc]
        if piece is None:
            return False

        target = self.board[tr][tc]
        if is_white(piece) and not self.turn_white:
            return False
        if is_black(piece) and self.turn_white:
            return False

        dr = tr - sr
        dc = tc - sc
        abs_dr = abs(dr)
        abs_dc = abs(dc)

        # Pawn moves
        if piece.upper() == 'P':
            direction = -1 if is_white(piece) else 1
            start_row = 6 if is_white(piece) else 1
            # Move forward
            if dc == 0 and target is None:
                if dr == direction:
                    return True
                if sr == start_row and dr == 2*direction and self.board[sr+direction][sc] is None:
                    return True
            # Capture
            if abs(dc) == 1 and dr == direction and target is not None:
                if (is_white(piece) and is_black(target)) or (is_black(piece) and is_white(target)):
                    return True
            return False

        # Knight moves
        if piece.upper() == 'N':
            if (abs_dr, abs_dc) in [(2,1),(1,2)]:
                if target is None or (is_white(piece) and is_black(target)) or (is_black(piece) and is_white(target)):
                    return True
            return False

        # Bishop moves
        if piece.upper() == 'B':
            if abs_dr == abs_dc and self.clear_path(sr, sc, tr, tc):
                if target is None or (is_white(piece) and is_black(target)) or (is_black(piece) and is_white(target)):
                    return True
            return False

        # Rook moves
        if piece.upper() == 'R':
            if (dr == 0 or dc == 0) and self.clear_path(sr, sc, tr, tc):
                if target is None or (is_white(piece) and is_black(target)) or (is_black(piece) and is_white(target)):
                    return True
            return False

        # Queen moves
        if piece.upper() == 'Q':
            if ((abs_dr == abs_dc) or (dr == 0 or dc == 0)) and self.clear_path(sr, sc, tr, tc):
                if target is None or (is_white(piece) and is_black(target)) or (is_black(piece) and is_white(target)):
                    return True
            return False

        # King moves
        if piece.upper() == 'K':
            if max(abs_dr, abs_dc) == 1:
                if target is None or (is_white(piece) and is_black(target)) or (is_black(piece) and is_white(target)):
                    return True
            return False

        return False

    def clear_path(self, sr, sc, tr, tc):
        dr = tr - sr
        dc = tc - sc
        step_r = 0 if dr == 0 else (1 if dr>0 else -1)
        step_c = 0 if dc == 0 else (1 if dc>0 else -1)
        r = sr + step_r
        c = sc + step_c
        while (r,c) != (tr,tc):
            if self.board[r][c] is not None:
                return False
            r += step_r
            c += step_c
        return True

    def is_king_captured(self):
        white_king = False
        black_king = False
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == 'K':
                    white_king = True
                if piece == 'k':
                    black_king = True
        return not (white_king and black_king)

if __name__ == '__main__':
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
