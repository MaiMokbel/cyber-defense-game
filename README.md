# Cyber-Defence Game: Minimax and Alpha-Beta Search

Two-player zero-sum game on a 10-host network. An attacker starting at the
Internet (H0) tries to reach and exfiltrate the database H5. A defender, with
a budget of 10, patches, isolates or restores hosts. The game lasts at most
10 plies. Three adversarial search algorithms choose the moves:

1. Minimax (full depth)
2. Depth-limited minimax (3 plies, with an evaluation function)
3. Alpha-beta pruning (full depth and 3 plies)

## Requirements

- Python 3.10 or newer (developed and tested on Python 3.12)
- `pytest` for the tests, `matplotlib` for the charts only

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Project structure

```
game/         network.py (hosts, edges), state.py (GameState), rules.py (actions, utility)
algorithms/   common.py (stats, ordering, evaluation), minimax.py,
              depth_limited.py, alphabeta.py
experiments/  states.py (fixed initial states), run_experiments.py
tests/        test_game.py (Task 1), test_algorithms.py (Task 2)
results/      CSV tables, summary.md and charts written by the experiments
report/       report PDF
```

## Run the tests

```bash
python -m pytest -v
```

## Play with the algorithms

```python
from game.state import initial_state
from algorithms.alphabeta import alphabeta
from algorithms.minimax import minimax
from algorithms.depth_limited import depth_limited_minimax

s = initial_state()
r = alphabeta(s, depth=None, ordering="smart")   # full depth
print(r.move, r.value, r.expanded, r.pruned, r.time_s)
r = depth_limited_minimax(s)                     # depth 3
```

`ordering` is `"naive"` (order produced by `legal_actions`) or `"smart"`
(domain-knowledge ordering, see `algorithms/common.py`). `depth=None` means
search to the end of the game.

## Run the experiments

```bash
pip install matplotlib
python -m experiments.run_experiments           # full run, a few minutes
python -m experiments.run_experiments --quick   # skips the slowest runs
```

Outputs go to `results/`: `comparison.csv`, `depth_sweep.csv`, `selfplay.csv`,
`summary.md`, `nodes_per_state.png` and `scalability.png`. The slowest run is
full-depth minimax from the official start (about 8 million nodes).

## Assumptions 

- A `Pass` counts as a ply, and so does `Exfiltrate`; the game ends right after
  it.
- Attacker moves on even plies, defender on odd plies.
- A connection is active only if neither end is isolated. An isolated
  compromised host keeps its value in the score but cannot spread, and nothing
  can spread into an isolated host.
- `Restore` makes a host clean and patched and does not undo isolation.
- H0 is never a target of any action.
- Search values are the defender's utility U; the attacker minimises it.

