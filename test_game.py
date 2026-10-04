"""Quick self-tests: python test_game.py"""
import random
from game import TicTacToe
from minimax import MinimaxSearch
from heuristic import HEURISTICS


def parse(rows):
    """'XO.' style strings -> board with '' for empty."""
    g = TicTacToe()
    g.board = [[('' if ch == '.' else ch) for ch in row] for row in rows]
    return g


def test_rules():
    g = TicTacToe()
    assert len(g.get_valid_moves()) == 9 and not g.is_terminal()
    for m in [(0, 0), (0, 1), (0, 2)]:
        g.make_move(m, 'X')
    assert g.check_winner() == 'X' and g.is_terminal()
    assert parse(["XOX", "XOO", "OXX"]).is_draw()
    try:
        g.make_move((0, 0), 'O'); assert False
    except ValueError:
        pass


def test_alpha_beta_same_decision():
    """Alpha-Beta must give EXACTLY the same scores as plain Minimax."""
    rng = random.Random(1)
    for name, h in HEURISTICS.items():
        for _ in range(40):
            g, turn = TicTacToe(), 'X'
            for _ in range(rng.randint(0, 5)):
                if g.is_terminal(): break
                g.make_move(rng.choice(g.get_valid_moves()), turn)
                turn = 'O' if turn == 'X' else 'X'
            if g.is_terminal(): continue
            for depth in (1, 2, 3, 4):
                a, sa = MinimaxSearch(h, True).search(g, turn, depth)
                b, sb = MinimaxSearch(h, False).search(g, turn, depth)
                assert a == b
                assert sa.nodes_evaluated <= sb.nodes_evaluated


def test_blocks_and_wins():
    from agents import make_nexus, make_titan
    for mk in (make_nexus, make_titan):
        for depth in (1, 2, 3, 4):
            g = parse(["XX.", "O..", "O.."])
            assert mk(depth, seed=0).choose_move(g, 'X') == (0, 2)   # take the win
            g = parse(["OO.", ".X.", "X.."])
            assert mk(depth, seed=0).choose_move(g, 'X') == (0, 2)   # block


if __name__ == "__main__":
    test_rules(); test_alpha_beta_same_decision(); test_blocks_and_wins()
    print("all tests passed")
