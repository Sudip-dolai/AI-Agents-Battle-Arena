"""game.py - Tic-Tac-Toe board and rules (no AI in here)."""

LINES = [
    [(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],  # rows
    [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],  # columns
    [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)],                            # diagonals
]


def opponent_of(player):
    return 'O' if player == 'X' else 'X'


class TicTacToe:
    """3x3 Tic-Tac-Toe. Empty cells are stored as '' (empty string)."""

    def __init__(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]

    # ---- queries -------------------------------------------------------
    def get_valid_moves(self):
        """Return list of (row, col) for every empty cell."""
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == '']

    def check_winner(self):
        """Return 'X' or 'O' if someone has three in a line, else None."""
        for line in LINES:
            a, b, c = (self.board[r][col] for r, col in line)
            if a != '' and a == b == c:
                return a
        return None

    def is_draw(self):
        return self.check_winner() is None and not self.get_valid_moves()

    def is_terminal(self):
        """Game over = somebody won or the board is full."""
        return self.check_winner() is not None or not self.get_valid_moves()

    # ---- actions -------------------------------------------------------
    def make_move(self, move, player):
        r, c = move
        if self.board[r][c] != '':
            raise ValueError(f"Cell {move} is already occupied")
        self.board[r][c] = player

    def undo_move(self, move):
        r, c = move
        self.board[r][c] = ''

    def copy(self):
        g = TicTacToe()
        g.board = [row[:] for row in self.board]
        return g

    # ---- display -------------------------------------------------------
    def display(self):
        rows = []
        for r in range(3):
            rows.append(' ' + ' | '.join(self.board[r][c] or ' ' for c in range(3)))
        print('\n---+---+---\n'.join(rows) + '\n')

    def __str__(self):
        return '\n'.join(' '.join(cell or '.' for cell in row) for row in self.board)
