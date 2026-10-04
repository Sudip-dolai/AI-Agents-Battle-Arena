"""heuristic.py - Static evaluation of NON-terminal positions.

Every heuristic has the signature  h(board, player) -> float  and returns a score
from `player`'s point of view (positive = good for `player`).
Scores are capped at +-80 (< any real win/loss, which is >= 91 in size) so they never beat a real win/loss.

H1 "Line Counter"   : purely counts open winning lines (tactical view).
H2 "Positional"     : square-value table + threats + fork detection (positional view).
"""
from game import LINES

WIN_SCORE = 100
HEUR_CAP = 80   # heuristic never gets close to a real win/loss (>= 91)


def _opp(p):
    return 'O' if p == 'X' else 'X'


def _line_contents(board, line):
    return [board[r][c] for r, c in line]


# ---------------------------------------------------------------- H1 -----
def h1_line_counter(board, player):
    """Score every line that is still winnable by only one side.

    own 1 mark (rest empty)  : +1      opp 1 mark : -1
    own 2 marks (a threat)   : +10     opp 2 marks: -10
    Lines that contain both X and O are dead and count as 0.
    """
    opp = _opp(player)
    score = 0
    for line in LINES:
        cells = _line_contents(board, line)
        mine, theirs = cells.count(player), cells.count(opp)
        if mine and theirs:
            continue
        if mine == 1:
            score += 1
        elif mine == 2:
            score += 10
        elif theirs == 1:
            score -= 1
        elif theirs == 2:
            score -= 10
    return max(-HEUR_CAP, min(HEUR_CAP, score))


# ---------------------------------------------------------------- H2 -----
POSITION_WEIGHTS = [[3, 2, 3],
                    [2, 4, 2],
                    [3, 2, 3]]   # centre > corners > edges (each cell sits in 4 / 3 / 2 lines)


def _fork_count(board, player):
    """Number of empty cells where `player` would create two threats at once."""
    forks = 0
    for r in range(3):
        for c in range(3):
            if board[r][c] != '':
                continue
            threats = 0
            for line in LINES:
                if (r, c) not in line:
                    continue
                cells = _line_contents(board, line)
                # after playing here the line would hold 2 of ours + 1 empty
                if cells.count(player) == 1 and cells.count('') == 2:
                    threats += 1
            if threats >= 2:
                forks += 1
    return forks


def h2_positional(board, player):
    """Position-weighted material + immediate threats + fork potential."""
    opp = _opp(player)
    score = 0
    # 1) square values (centre/corner control)
    for r in range(3):
        for c in range(3):
            if board[r][c] == player:
                score += POSITION_WEIGHTS[r][c]
            elif board[r][c] == opp:
                score -= POSITION_WEIGHTS[r][c]
    # 2) immediate threats: two in a line with the third cell empty
    for line in LINES:
        cells = _line_contents(board, line)
        if cells.count(player) == 2 and cells.count('') == 1:
            score += 12
        elif cells.count(opp) == 2 and cells.count('') == 1:
            score -= 12
    # 3) fork potential (squares that would create a double threat)
    score += 5 * _fork_count(board, player)
    score -= 5 * _fork_count(board, opp)
    return max(-HEUR_CAP, min(HEUR_CAP, score))


HEURISTICS = {'H1': h1_line_counter, 'H2': h2_positional}
