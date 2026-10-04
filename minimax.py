"""minimax.py - Minimax with optional Alpha-Beta pruning and node counters."""
from dataclasses import dataclass
from game import opponent_of
from heuristic import WIN_SCORE


@dataclass
class SearchStats:
    nodes_evaluated: int = 0   # every position the search visits
    nodes_pruned: int = 0      # child positions skipped thanks to an alpha-beta cut-off

    def add(self, other):
        self.nodes_evaluated += other.nodes_evaluated
        self.nodes_pruned += other.nodes_pruned


class MinimaxSearch:
    """Depth-limited Minimax. depth is a PARAMETER of search(), never hard-coded.

    Terminal scores: win +100, draw 0, loss -100 (from the root player's view),
    with a 1-point-per-move bonus for winning sooner / losing later (win in 3
    plies = 97). Without it the AI may "toy" with a won position instead of
    finishing it, because every winning line scores the same.
    At depth 0 on a non-terminal board the injected heuristic is used instead.
    """

    def __init__(self, heuristic, use_alpha_beta=True):
        self.heuristic = heuristic
        self.use_alpha_beta = use_alpha_beta
        self.stats = SearchStats()

    def search(self, game, player, depth):
        """Score every legal root move. Returns ({move: score}, SearchStats).

        Each root move is searched with a FULL (-inf, +inf) window so every root
        score is exact - this lets the agent tell true ties apart and choose
        randomly among them. Pruning still happens everywhere below the root.
        """
        self.stats = SearchStats()
        scores = {}
        for move in game.get_valid_moves():
            game.make_move(move, player)
            scores[move] = self._value(game, depth - 1, float('-inf'), float('inf'),
                                       maximizing=False, root=player, ply=1)
            game.undo_move(move)
        return scores, self.stats

    def _value(self, game, depth, alpha, beta, maximizing, root, ply):
        self.stats.nodes_evaluated += 1
        winner = game.check_winner()
        if winner is not None:
            return (WIN_SCORE - ply) if winner == root else -(WIN_SCORE - ply)
        moves = game.get_valid_moves()
        if not moves:
            return 0                                   # draw
        if depth <= 0:
            return self.heuristic(game.board, root)    # horizon reached

        mover = root if maximizing else opponent_of(root)
        best = float('-inf') if maximizing else float('inf')
        for i, move in enumerate(moves):
            game.make_move(move, mover)
            val = self._value(game, depth - 1, alpha, beta, not maximizing, root, ply + 1)
            game.undo_move(move)
            if maximizing:
                best = max(best, val)
                alpha = max(alpha, best)
            else:
                best = min(best, val)
                beta = min(beta, best)
            if self.use_alpha_beta and beta <= alpha:
                self.stats.nodes_pruned += len(moves) - i - 1   # siblings never visited
                break
        return best
