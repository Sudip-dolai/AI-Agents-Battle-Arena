# AI Agent Battle — Tic-Tac-Toe (AI/ML Lab, Assignment X_02)

Two named AI agents, **NEXUS** and **TITAN**, play Tic-Tac-Toe against each other with
Minimax + Alpha-Beta pruning, each using a *different* heuristic. No human player, no external AI libraries
(pure Python standard library).

## How to run
```bash
python test_game.py                       # self-tests (rules, alpha-beta == minimax, win/block)
python main.py                            # Experiment 1 (depth) + Experiment 2 (10-game battle) + analysis
python main.py --mode battle --depth 3    # only the battle (try --depth-nexus 4 --depth-titan 2)
python main.py --mode demo                # watch one game move by move
python main.py --seed 7                   # different random tie-breaks
```
Outputs go to `results/`: `results.csv` (10-game battle), `depth_results.csv` (depth experiment),
`extra_depth1/`, `extra_depth2/` (the same battle run at depth 1 and 2), `console_output.txt`.
Summary numbers (wins, draws, averages) are **computed by re-reading the CSV**, not from printed values.

## Project structure
| File | Responsibility |
|---|---|
| `game.py` | `TicTacToe` class: board, valid moves, make/undo move, winner, draw, terminal, display |
| `heuristic.py` | H1 and H2 evaluation functions (`h(board, player)`) |
| `minimax.py` | `MinimaxSearch`: Minimax + Alpha-Beta (switchable), node counters; depth is a *parameter* |
| `agents.py` | `Agent` class (name, depth, heuristic, `choose_move`, `evaluate`) + `make_nexus`, `make_titan` |
| `experiment.py` | `Experiment` class (`run_game`, `run_multiple_games`, `save_results`, `analyse_results`) + depth experiment |
| `main.py` | command-line entry point |
| `test_game.py` | self-tests |

## Agents
| Agent | Algorithm | Heuristic | Depth |
|---|---|---|---|
| **NEXUS** | Minimax + Alpha-Beta | **H1 – Line Counter** (tactical) | 3 (configurable) |
| **TITAN** | Minimax + Alpha-Beta | **H2 – Positional** (strategic) | 3 (configurable) |

### Search
* MAX = the agent to move, MIN = the opponent. Terminal: win ≈ +100, draw 0, loss ≈ −100.
  I subtract 1 point per ply (win in 3 plies = 97), so the agent prefers *faster* wins / slower losses.
  Without it, every winning line scores exactly 100 and the agent could randomly delay a win it already has
  (I actually hit this bug in testing: at depth 3 the agent did not take an immediate win).
* At the depth limit on an unfinished board, the heuristic is used (capped at ±80, so it can never outrank a real win/loss).
* **Depth is never hard-coded**: `search(game, player, depth)`; change `--depth`.
* **Alpha-Beta** is switchable (`use_alpha_beta`). `test_game.py` verifies it returns *exactly the same root scores*
  as plain Minimax at depths 1–4 for both heuristics, i.e. it only changes efficiency, not the decision.
* **Counters**: `nodes_evaluated` = every position the search visits; `nodes_pruned` = child positions skipped by a cut-off.
* Each root move is searched with a full (−∞,+∞) window so root scores are exact; equally-scored moves are chosen
  **randomly** (seeded, reproducible), as the assignment allows. Pruning applies everywhere below the root.

### Heuristics
* **H1 Line Counter (NEXUS)** – looks at the 8 lines. A line still open for only one side: own 1 mark `+1`, own 2 marks `+10`;
  opponent 1 mark `−1`, 2 marks `−10`. Dead lines (both X and O) = 0.
* **H2 Positional (TITAN)** – square values (centre 4, corners 3, edges 2: roughly how many lines the square sits on)
  + immediate threats (`±12` for two-in-line with the third empty) + fork potential (`±5` per empty square that would create two threats at once).

Both are reasonable and comparable; neither is deliberately weak.

## Experiment 1 — Does thinking deeper help?
Fixed: game, Minimax+Alpha-Beta, heuristic H1. Only NEXUS's depth changes (1–4). Each depth plays 10 games
(alternating first player) against a fixed TITAN (H2): first a **strong** reference (depth 3) and then a **weak** one (depth 1).
Nodes/pruned/time are NEXUS's totals over the 10 games. The last columns show the cost of the *same* opening decision
(empty board) with and without pruning.

| Ref depth | NEXUS depth | W-D-L | Nodes evaluated | Nodes pruned | Time (s) | Opening nodes, Alpha-Beta | Opening nodes, plain Minimax |
|---|---|---|---|---|---|---|---|
| 3 | 1 | 0-10-0 | 225 | 0 | 0.087 | 9 | 9 |
| 3 | 2 | 0-10-0 | 1,425 | 0 | 0.107 | 81 | 81 |
| 3 | 3 | 0-10-0 | 4,596 | 2,929 | 0.116 | 308 | 585 |
| 3 | 4 | 0-10-0 | 16,347 | 6,415 | 0.201 | 1,315 | 3,609 |
| 1 | 1 | 6-4-0 | 218 | 0 | 0.008 | 9 | 9 |
| 1 | 2 | 4-6-0 | 1,397 | 0 | 0.018 | 81 | 81 |
| 1 | 3 | 4-6-0 | 4,691 | 2,866 | 0.039 | 308 | 585 |
| 1 | 4 | 9-1-0 | 16,570 | 6,444 | 0.147 | 1,315 | 3,609 |

(Timings are machine-dependent; node counts are exact for seed 42.)

### Discussion
* **Cost grows fast.** Nodes grow ≈ 6× per extra ply at the start (225 → 1,425 → 4,596 → 16,347 total), and time rose from ~0.09 s to ~0.20 s
  (vs depth-3 TITAN). Tic-Tac-Toe is tiny; in a bigger game this exponential growth is the real limit.
* **Pruning only appears from depth 3.** At depth 1–2 nothing can be pruned (a cut-off needs at least a MAX level below a MIN level
  *under* the root, and my root uses a full window). From depth 3 it saves ≈ 47 % (308 vs 585) of the opening nodes and ≈ 64 % at depth 4 (1,315 vs 3,609).
  The saving gets bigger with depth.
* **Playing strength is not a clean "deeper = better" line.** Against the strong reference every depth drew all 10 games
  (Tic-Tac-Toe is a draw with sensible play, so extra depth cannot show up as extra wins). Against the weak reference
  depth 4 was best (9 wins) but depth 2 and 3 (4 wins each) were *worse* than depth 1 (6 wins). With only 10 games and random tie-breaking
  I do **not** claim this is a real effect; likely explanation: a heuristic tuned for shallow evaluation plus the fact that
  a mid-depth search sees "safe" draws and stops trying to set traps. Deeper search changes the *quality* of decisions, but on this small game
  mostly in avoiding losses, not in creating wins.
* **Decisions:** all four depths choose the centre (cell 1,1) as the opening move, so for that decision more depth changed nothing — just the price.

## Experiment 2 — NEXUS (H1, depth 3) vs TITAN (H2, depth 3), 10 games
Games alternate starting player (odd = NEXUS, even = TITAN). Raw data: `results/results.csv`.

| Game | First | Winner | Moves | NEXUS nodes | TITAN nodes |
|---|---|---|---|---|---|
| 1 | NEXUS | DRAW | 9 | 544 | 367 |
| 2 | TITAN | DRAW | 9 | 364 | 558 |
| 3 | NEXUS | DRAW | 9 | 579 | 393 |
| 4 | TITAN | DRAW | 9 | 358 | 544 |
| 5 | NEXUS | DRAW | 9 | 545 | 358 |
| 6 | TITAN | DRAW | 9 | 370 | 557 |
| 7 | NEXUS | DRAW | 9 | 544 | 367 |
| 8 | TITAN | DRAW | 9 | 378 | 565 |
| 9 | NEXUS | DRAW | 9 | 544 | 367 |
| 10 | TITAN | DRAW | 9 | 370 | 557 |

**Summary (computed from the CSV):** NEXUS 0 wins, TITAN 0 wins, **10 draws**. Average nodes per game: NEXUS 459.6, TITAN 463.3.
Average pruned per game: NEXUS 292.9, TITAN 289.2. Average length 9 moves. Average time 0.0115 s/game (0.115 s total).

### Extra battles (same code, different depth)
| Depth (both) | NEXUS wins | TITAN wins | Draws | Avg nodes N / T | Avg moves |
|---|---|---|---|---|---|
| 1 | 6 | 0 | 4 | 21.8 / 21.1 | 7.7 |
| 2 | 0 | 0 | 10 | 142.5 / 142.5 | 9.0 |
| 3 (main) | 0 | 0 | 10 | 459.6 / 463.3 | 9.0 |

## Analysis (assignment questions)
**About depth**
1. *Did depth change decisions?* In the battle, yes: depth 1 gave decisive games (NEXUS 6 wins), depth 2 and 3 gave only draws. For the empty-board opening, no: always centre.
2. *Execution time?* Yes, it rose with depth (0.087 → 0.201 s per 10 games for NEXUS at depths 1 → 4).
3. *Nodes?* Yes, strongly: 225 → 1,425 → 4,596 → 16,347.
4. *Did Alpha-Beta reduce nodes?* Yes from depth 3 on (−47 % at depth 3, −64 % at depth 4 for the opening search), and the decision is identical (tested). At depth 1–2 it cannot prune anything.

**About the agents**
5. *Different decisions?* Yes. Moves are identical in the opening (both take the centre) but diverge afterwards: the 10 games produced 6 distinct move sequences (games with the same starter often repeat, since only ties are random).
6. *Heuristic influence?* H1 and H2 both rate "take the centre, block threats" highly, so at depth ≥ 2 the search itself (seeing forced wins/losses) dominates and they converge to the same drawing play. The heuristic matters most when the horizon is short: at depth 1, where it is the only guide, H1 beat H2 six times and never lost, so in this setup the line-counting view was better than the positional one at depth 1. I did not test *why* in detail (e.g. which H2 term hurts).
7. *First-player advantage?* Not visible at depth 3 (no one won). At depth 1, 5 of the 6 decisive games were won by the first mover, but NEXUS also won one game as second player, so this is mixed with agent strength. In theory perfect play draws.
8. *Who won more?* At depth 3: nobody (0–0). At depth 1: NEXUS (6–0).
9. *Many draws?* Yes — 10/10 at depth 3, 10/10 at depth 2, 4/10 at depth 1. Two competent searchers on Tic-Tac-Toe are expected to draw.
10. *Did the winner use more computation?* At depth 1 NEXUS (winner) used 21.8 nodes/game vs 21.1 for TITAN — essentially the same. A clear pattern is that **whoever moves first evaluates more nodes** (e.g. 544 vs 367): the first player moves on emptier boards and makes 5 moves instead of 4. So node counts reflect move order more than agent quality.

## Conclusion
Alpha-Beta gives the same decisions as Minimax with fewer nodes (up to about two-thirds fewer here), and cost grows roughly exponentially with depth. On
Tic-Tac-Toe, deeper search mainly protects against losing; once both agents search 2–3 plies the game is a draw regardless of heuristic.
Heuristic differences only changed outcomes at depth 1. With 10 games per setting, small differences (e.g. depth 2/3 vs 1 against the weak
reference) may be noise, so I treat them as observations, not proof. Neither agent can be called "better" at depth 3: the evidence is 10 draws.

## Limitations / ideas
* 10 games with a seeded RNG; a different `--seed` gives different tie-breaks (run more games with `--games 100` for stronger evidence).
* Heuristic weights were set by hand and not tuned.
* Possible extension: move ordering (centre first) to improve pruning.
