"""agents.py - Named AI agents (NEXUS and TITAN)."""
import random
from game import TicTacToe
from heuristic import HEURISTICS
from minimax import MinimaxSearch, SearchStats


class Agent:
    def __init__(self, name, depth, heuristic_name, use_alpha_beta=True, seed=None):
        self.name = name
        self.depth = depth                      # configurable search depth
        self.heuristic_name = heuristic_name
        self.heuristic = HEURISTICS[heuristic_name]
        self.search = MinimaxSearch(self.heuristic, use_alpha_beta)
        self.rng = random.Random(seed)
        self.stats = SearchStats()              # accumulated since last reset

    def evaluate(self, board, player):
        """Static evaluation of a board with this agent's heuristic."""
        return self.heuristic(board, player)

    def choose_move(self, game, player):
        scores, stats = self.search.search(game, player, self.depth)
        self.stats.add(stats)
        best = max(scores.values())
        # equally good moves -> random pick (different games, no weakness)
        return self.rng.choice([m for m, s in scores.items() if s == best])

    def reset_stats(self):
        self.stats = SearchStats()

    def __repr__(self):
        return f"{self.name}(depth={self.depth}, {self.heuristic_name})"


def make_nexus(depth=3, seed=None, use_alpha_beta=True):
    """NEXUS - tactical thinker: counts open winning lines (H1)."""
    return Agent("NEXUS", depth, "H1", use_alpha_beta, seed)


def make_titan(depth=3, seed=None, use_alpha_beta=True):
    """TITAN - positional thinker: centre/corner control, threats, forks (H2)."""
    return Agent("TITAN", depth, "H2", use_alpha_beta, seed)
