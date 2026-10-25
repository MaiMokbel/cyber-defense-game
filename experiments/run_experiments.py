"""Run all experiments and write CSV / Markdown / PNG files to results/.

Usage (from the repo root):
    python -m experiments.run_experiments            # everything (~6-8 min)
    python -m experiments.run_experiments --quick    # skips the slowest runs
"""
import argparse
import csv
import os
import platform
import statistics
import sys
import time

from algorithms.alphabeta import alphabeta
from algorithms.common import SearchResult
from algorithms.minimax import minimax
from experiments.states import EXPERIMENT_STATES
from game.rules import (DEFENDER, apply_action, current_player, is_terminal,
                        utility)

RESULTS_DIR = "results"
DEPTH_LIMIT = 3

ALGOS = {"minimax": minimax, "alphabeta": alphabeta}

# (algorithm, depth, ordering)
CONFIGS = [
    ("minimax", None, "naive"), ("minimax", None, "smart"),
    ("alphabeta", None, "naive"), ("alphabeta", None, "smart"),
    ("minimax", DEPTH_LIMIT, "naive"), ("minimax", DEPTH_LIMIT, "smart"),
    ("alphabeta", DEPTH_LIMIT, "naive"), ("alphabeta", DEPTH_LIMIT, "smart"),
]


def label(algo, depth):
    return algo if depth is None else f"{algo}-d{depth}"


def timed(algo, state, depth, ordering):
    """Median of up to 5 runs for fast searches, a single run for slow ones."""
    res = ALGOS[algo](state, depth, ordering)
    if res.time_s < 0.5:
        times = [res.time_s] + [ALGOS[algo](state, depth, ordering).time_s
                                for _ in range(4)]
        res.time_s = statistics.median(times)
    return res


def true_value_of_move(state, move, cache):
    """Exact (full-depth) value of the position reached by `move`."""
    child = apply_action(state, move)
    if child not in cache:
        cache[child] = alphabeta(child, None, "naive").value
    return cache[child]


def regret(state, move, optimal, cache):
    """How much worse (for the mover) the chosen move is than the best one."""
    if move is None:
        return 0
    v = true_value_of_move(state, move, cache)
    if current_player(state) == DEFENDER:
        return optimal - v
    return v - optimal


# --------------------------------------------------------- experiment 1
def comparison():
    rows, cache = [], {}
    for sname, (desc, state) in EXPERIMENT_STATES.items():
        optimal = alphabeta(state, None, "naive").value
        for algo, depth, ordering in CONFIGS:
            print(f"  {sname} {label(algo, depth):12s} {ordering}", flush=True)
            res = timed(algo, state, depth, ordering)
            # tracemalloc is ~3-10x slower, so it is skipped for searches that
            # already take more than 5 s (space is then given by max_depth).
            if res.time_s <= 5:
                mem = ALGOS[algo](state, depth, ordering,
                                  measure_memory=True).peak_mem_kb
            else:
                mem = None
            rows.append({
                "state": sname, "ply": state.ply,
                "algorithm": label(algo, depth), "ordering": ordering,
                "move": str(res.move), "value": res.value,
                "optimal_value": optimal,
                "regret": regret(state, res.move, optimal, cache),
                "expanded": res.expanded, "leaves": res.leaves,
                "visited": res.visited, "pruned": res.pruned,
                "max_depth": res.max_depth,
                "time_s": round(res.time_s, 5),
                "peak_mem_kb": None if mem is None else round(mem, 1),
            })
    return rows


# --------------------------------------------------------- experiment 2
def depth_sweep(max_minimax_depth):
    """Scalability: depth 1..10 from the official start."""
    state = EXPERIMENT_STATES["S0"][1]
    rows = []
    for depth in range(1, 11):
        for algo, ordering in [("minimax", "naive"), ("alphabeta", "naive"),
                               ("alphabeta", "smart")]:
            if algo == "minimax" and depth > max_minimax_depth:
                continue
            print(f"  depth {depth:2d} {algo} {ordering}", flush=True)
            res = timed(algo, state, depth, ordering)
            rows.append({"depth": depth, "algorithm": algo,
                         "ordering": ordering, "move": str(res.move),
                         "value": res.value, "expanded": res.expanded,
                         "visited": res.visited, "pruned": res.pruned,
                         "time_s": round(res.time_s, 5)})
    return rows


# --------------------------------------------------------- experiment 3
def self_play():
    """Full games from S0 with each side using optimal or depth-3 search."""
    players = {"optimal": None, "depth-3": DEPTH_LIMIT}
    rows = []
    for att_name, att_depth in players.items():
        for def_name, def_depth in players.items():
            state = EXPERIMENT_STATES["S0"][1]
            moves, nodes = [], 0
            while not is_terminal(state):
                depth = def_depth if current_player(state) == DEFENDER \
                    else att_depth
                res = alphabeta(state, depth, "naive")
                nodes += res.visited
                moves.append(str(res.move))
                state = apply_action(state, res.move)
            rows.append({"attacker": att_name, "defender": def_name,
                         "final_utility": utility(state),
                         "exfiltrated": state.exfiltrated,
                         "total_nodes": nodes,
                         "moves": " ".join(moves)})
    return rows


# ------------------------------------------------------------------ output
def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def md_table(rows, cols):
    out = ["| " + " | ".join(cols) + " |",
           "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows:
        out.append("| " + " | ".join(
            "-" if r[c] is None else str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def write_markdown(comp, sweep, play, meta):
    path = os.path.join(RESULTS_DIR, "summary.md")
    with open(path, "w") as f:
        f.write("# Experiment results\n\n## Setup\n\n")
        for k, v in meta.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## Initial states\n\n")
        for n, (d, s) in EXPERIMENT_STATES.items():
            f.write(f"- **{n}** - {d}\n")
        f.write("\n## Experiment 1: algorithm comparison\n\n")
        f.write(md_table(comp, ["state", "algorithm", "ordering", "move",
                                "value", "optimal_value", "regret",
                                "expanded", "leaves", "pruned", "max_depth",
                                "time_s", "peak_mem_kb"]))
        f.write("\n\n## Experiment 2: depth sweep from S0\n\n")
        f.write(md_table(sweep, ["depth", "algorithm", "ordering", "move",
                                 "value", "expanded", "visited", "pruned",
                                 "time_s"]))
        f.write("\n\n## Experiment 3: self-play from S0\n\n")
        f.write(md_table(play, ["attacker", "defender", "final_utility",
                                "exfiltrated", "total_nodes", "moves"]))
        f.write("\n")


def make_charts(comp, sweep):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: skipping charts")
        return

    # Chart 1: visited nodes per state (full-depth algorithms, log scale).
    fig, ax = plt.subplots(figsize=(8, 4.5))
    series = [("minimax", "naive"), ("alphabeta", "naive"),
              ("alphabeta", "smart")]
    states = list(EXPERIMENT_STATES)
    width = 0.27
    for i, (algo, order) in enumerate(series):
        vals = [next(r["visited"] for r in comp if r["state"] == s
                     and r["algorithm"] == algo and r["ordering"] == order)
                for s in states]
        ax.bar([x + (i - 1) * width for x in range(len(states))], vals,
               width, label=f"{algo} ({order})")
    ax.set_yscale("log")
    ax.set_xticks(range(len(states)))
    ax.set_xticklabels(states)
    ax.set_ylabel("nodes visited (log scale)")
    ax.set_title("Full-depth search: nodes visited per initial state")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "nodes_per_state.png"), dpi=150)
    plt.close(fig)

    # Chart 2: scalability with search depth.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for algo, order in series:
        pts = [(r["depth"], r["visited"], r["time_s"]) for r in sweep
               if r["algorithm"] == algo and r["ordering"] == order]
        axes[0].plot([p[0] for p in pts], [p[1] for p in pts], marker="o",
                     label=f"{algo} ({order})")
        axes[1].plot([p[0] for p in pts], [max(p[2], 1e-5) for p in pts],
                     marker="o", label=f"{algo} ({order})")
    for ax, yl in zip(axes, ["nodes visited", "time (s)"]):
        ax.set_yscale("log")
        ax.set_xlabel("search depth (plies)")
        ax.set_ylabel(yl + " (log scale)")
        ax.grid(True, which="both", alpha=0.3)
    axes[0].legend()
    fig.suptitle("Scalability from the official start state S0")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "scalability.png"), dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="limit the minimax depth sweep to 8 plies")
    args = ap.parse_args()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    t0 = time.time()

    print("Experiment 1: comparison")
    comp = comparison()
    write_csv(os.path.join(RESULTS_DIR, "comparison.csv"), comp)
    print("Experiment 2: depth sweep")
    sweep = depth_sweep(8 if args.quick else 10)
    write_csv(os.path.join(RESULTS_DIR, "depth_sweep.csv"), sweep)
    print("Experiment 3: self-play")
    play = self_play()
    write_csv(os.path.join(RESULTS_DIR, "selfplay.csv"), play)

    meta = {"Python": sys.version.split()[0],
            "Platform": platform.platform(),
            "Processor": platform.processor() or platform.machine(),
            "Depth limit": f"{DEPTH_LIMIT} plies",
            "Timing": "median of 5 runs if a run takes <0.5 s, else 1 run",
            "Memory": "tracemalloc peak in a separate run, skipped (-) when a "
                      "search takes >5 s; max_depth = recursion depth",
            "Quick mode": args.quick,
            "Total runtime": f"{time.time() - t0:.0f} s"}
    write_markdown(comp, sweep, play, meta)
    make_charts(comp, sweep)
    print(f"Done in {time.time() - t0:.0f} s. Files are in {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
