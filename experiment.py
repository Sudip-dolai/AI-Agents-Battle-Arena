"""experiment.py - Runs games, depth experiment, saves + analyses CSV results."""
import csv
import os
import time
from game import TicTacToe
from agents import make_nexus, make_titan, Agent
from minimax import MinimaxSearch
from heuristic import HEURISTICS

RESULTS_DIR = "results"
BATTLE_FIELDS = ["game", "first", "winner", "moves", "nexus_nodes", "titan_nodes",
                 "nexus_pruned", "titan_pruned", "time_sec", "move_sequence"]
DEPTH_FIELDS = ["ref_depth", "depth", "games", "wins", "draws", "losses", "nodes_evaluated",
                "nodes_pruned", "time_sec", "nodes_ab_opening", "nodes_no_pruning_opening",
                "nodes_pruned_opening", "opening_best_moves"]


class Experiment:
    def __init__(self, agent_a, agent_b, results_dir=RESULTS_DIR):
        self.a, self.b = agent_a, agent_b
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)

    # ---- one game ------------------------------------------------------
    def run_game(self, first, second, verbose=False):
        """`first` plays X and moves first. Returns a stats dict."""
        for ag in (first, second):
            ag.reset_stats()
        game = TicTacToe()
        marks = {first.name: 'X', second.name: 'O'}
        by_mark = {'X': first, 'O': second}
        turn, history = 'X', []
        t0 = time.perf_counter()
        while not game.is_terminal():
            move = by_mark[turn].choose_move(game, turn)
            game.make_move(move, turn)
            history.append(f"{turn}{move[0]}{move[1]}")
            if verbose:
                print(f"{by_mark[turn].name} ({turn}) -> {move}")
                game.display()
            turn = 'O' if turn == 'X' else 'X'
        elapsed = time.perf_counter() - t0
        w = game.check_winner()
        winner = "DRAW" if w is None else by_mark[w].name
        return {"first": first.name, "winner": winner, "moves": len(history),
                "time_sec": round(elapsed, 4), "move_sequence": " ".join(history),
                f"{first.name}_stats": first.stats, f"{second.name}_stats": second.stats}

    # ---- 10-game battle ------------------------------------------------
    def run_multiple_games(self, n=10, verbose=False):
        rows = []
        for g in range(1, n + 1):
            first, second = (self.a, self.b) if g % 2 == 1 else (self.b, self.a)
            r = self.run_game(first, second, verbose)
            sa, sb = r[f"{self.a.name}_stats"], r[f"{self.b.name}_stats"]
            rows.append({"game": g, "first": r["first"], "winner": r["winner"],
                         "moves": r["moves"],
                         "nexus_nodes": sa.nodes_evaluated, "titan_nodes": sb.nodes_evaluated,
                         "nexus_pruned": sa.nodes_pruned, "titan_pruned": sb.nodes_pruned,
                         "time_sec": r["time_sec"], "move_sequence": r["move_sequence"]})
        return rows

    def save_results(self, rows, filename="results.csv", fields=BATTLE_FIELDS):
        path = os.path.join(self.results_dir, filename)
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        return path

    # ---- read CSV back and compute summary -----------------------------
    @staticmethod
    def analyse_results(path):
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        n = len(rows)
        names = ("NEXUS", "TITAN")
        s = {"games": n,
             "wins": {nm: sum(r["winner"] == nm for r in rows) for nm in names},
             "draws": sum(r["winner"] == "DRAW" for r in rows),
             "wins_by_first_mover": sum(r["winner"] == r["first"] for r in rows),
             "wins_by_second_mover": sum(r["winner"] not in ("DRAW", r["first"]) for r in rows)}
        for col in ("nexus_nodes", "titan_nodes", "nexus_pruned", "titan_pruned", "moves", "time_sec"):
            s["avg_" + col] = sum(float(r[col]) for r in rows) / n
        s["total_time_sec"] = sum(float(r["time_sec"]) for r in rows)
        return s


# ------------------------------------------------------------------------
# Experiment 1: effect of search depth (game, algorithm, heuristic fixed = H1)
# ------------------------------------------------------------------------
def depth_experiment(depths=(1, 2, 3, 4), games=10, ref_depth=3, seed=42,
                     results_dir=RESULTS_DIR):
    """NEXUS (H1) with depth d plays `games` games against a fixed reference
    opponent (TITAN, H2, depth `ref_depth`). Only d changes between rows.
    Nodes/pruned/time are NEXUS's own totals over those games."""
    rows = []
    for d in depths:
        nexus = make_nexus(depth=d, seed=seed)
        ref = make_titan(depth=ref_depth, seed=seed + 1)
        exp = Experiment(nexus, ref, results_dir)
        wins = draws = losses = nodes = pruned = 0
        t_total = 0.0
        for g in range(1, games + 1):
            first, second = (nexus, ref) if g % 2 == 1 else (ref, nexus)
            r = exp.run_game(first, second)
            st = r["NEXUS_stats"]
            nodes += st.nodes_evaluated
            pruned += st.nodes_pruned
            t_total += r["time_sec"]
            if r["winner"] == "DRAW": draws += 1
            elif r["winner"] == "NEXUS": wins += 1
            else: losses += 1
        # same opening decision (empty board, X to move), with and without pruning
        empty = TicTacToe()
        sc, st_ab = MinimaxSearch(HEURISTICS["H1"], True).search(empty, 'X', d)
        sc2, st_plain = MinimaxSearch(HEURISTICS["H1"], False).search(empty, 'X', d)
        assert sc == sc2, "Alpha-Beta must not change minimax scores!"
        best = max(sc.values())
        rows.append({"ref_depth": ref_depth, "depth": d, "games": games, "wins": wins, "draws": draws, "losses": losses,
                     "nodes_evaluated": nodes, "nodes_pruned": pruned,
                     "time_sec": round(t_total, 4),
                     "nodes_ab_opening": st_ab.nodes_evaluated,
                     "nodes_no_pruning_opening": st_plain.nodes_evaluated,
                     "nodes_pruned_opening": st_ab.nodes_pruned,
                     "opening_best_moves": " ".join(f"{m[0]}{m[1]}" for m, s in sc.items() if s == best)})
    return rows
