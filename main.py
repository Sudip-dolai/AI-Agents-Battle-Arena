"""main.py - command-line entry point.

Usage:
    python main.py                      # depth experiment + 10-game battle + analysis
    python main.py --mode battle --games 10 --depth 3 --verbose
    python main.py --mode depth
    python main.py --mode demo          # watch one game move by move
"""
import argparse
from agents import make_nexus, make_titan
from experiment import Experiment, depth_experiment, DEPTH_FIELDS


def run_depth(args):
    print("\n=== EXPERIMENT 1: search depth (NEXUS/H1 depth d vs fixed TITAN/H2 reference) ===")
    rows = []
    for ref in (3, 1):      # strong reference (depth 3) and weak reference (depth 1)
        rows += depth_experiment(games=args.games, ref_depth=ref, seed=args.seed, results_dir=args.out)
    path = Experiment(make_nexus(), make_titan(), args.out).save_results(rows, "depth_results.csv", DEPTH_FIELDS)
    print(f"{'Ref':>3} {'Depth':>5} {'W-D-L':>8} {'Nodes':>9} {'Pruned':>9} {'Time(s)':>8} "
          f"{'Opening nodes (AB)':>19} {'(no AB)':>9}")
    for r in rows:
        print(f"{r['ref_depth']:>3} {r['depth']:>5} {str(r['wins'])+'-'+str(r['draws'])+'-'+str(r['losses']):>8} {r['nodes_evaluated']:>9} "
              f"{r['nodes_pruned']:>9} {r['time_sec']:>8} {r['nodes_ab_opening']:>19} "
              f"{r['nodes_no_pruning_opening']:>9}")
    print("saved ->", path)


def run_battle(args):
    nexus = make_nexus(args.depth_nexus or args.depth, seed=args.seed)
    titan = make_titan(args.depth_titan or args.depth, seed=args.seed + 1)
    exp = Experiment(nexus, titan, args.out)
    print(f"\n=== EXPERIMENT 2: {nexus} vs {titan} ===")
    rows = exp.run_multiple_games(args.games, args.verbose)
    path = exp.save_results(rows)
    print(f"{'Game':>4} {'First':>6} {'Winner':>6} {'Moves':>5} {'NEXUS nodes':>11} {'TITAN nodes':>11} {'Time(s)':>8}")
    for r in rows:
        print(f"{r['game']:>4} {r['first']:>6} {r['winner']:>6} {r['moves']:>5} "
              f"{r['nexus_nodes']:>11} {r['titan_nodes']:>11} {r['time_sec']:>8}")
    s = Experiment.analyse_results(path)          # computed from the saved CSV
    print("\n--- Summary (computed from", path, ") ---")
    for k, v in s.items():
        print(f"{k}: {round(v, 3) if isinstance(v, float) else v}")


def main():
    p = argparse.ArgumentParser(description="AI Agent Battle - Tic-Tac-Toe")
    p.add_argument("--mode", choices=["all", "battle", "depth", "demo"], default="all")
    p.add_argument("--games", type=int, default=10)
    p.add_argument("--depth", type=int, default=3, help="depth for both agents")
    p.add_argument("--depth-nexus", type=int, default=None)
    p.add_argument("--depth-titan", type=int, default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="results")
    p.add_argument("--verbose", action="store_true")
    a = p.parse_args()
    if a.mode == "demo":
        a.games, a.verbose = 1, True
        a.out = "results/demo"      # keep the demo away from the real results.csv
        run_battle(a)
        return
    if a.mode in ("all", "depth"): run_depth(a)
    if a.mode in ("all", "battle"): run_battle(a)


if __name__ == "__main__":
    main()
