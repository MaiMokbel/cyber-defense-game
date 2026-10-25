"""Shared search infrastructure: statistics, action ordering, evaluation."""
import heapq
import time
import tracemalloc
from collections import deque
from dataclasses import dataclass
from typing import Callable, List, Optional

from game.network import ASSET_VALUE, NEIGHBORS, NUM_HOSTS, TARGET
from game.rules import (DEFENDER, Action, apply_action, current_player,
                        is_terminal, legal_actions, utility)
from game.state import MAX_PLIES, GameState

# --------------------------------------------------------------- statistics
@dataclass
class SearchResult:
    algorithm: str
    ordering: str
    depth: Optional[int]          # plies searched (None = to the end of game)
    move: Optional[Action]
    value: float                  # defender utility U of the root position
    expanded: int = 0             # internal nodes (successors generated)
    leaves: int = 0               # terminal or depth-cutoff nodes evaluated
    pruned: int = 0               # branches skipped by alpha-beta cutoffs
    max_depth: int = 0            # deepest ply reached (= recursion depth)
    time_s: float = 0.0
    peak_mem_kb: Optional[float] = None

    @property
    def visited(self) -> int:
        return self.expanded + self.leaves


class Counter:
    """Mutable counters threaded through one search."""
    def __init__(self):
        self.expanded = self.leaves = self.pruned = self.max_depth = 0


# ----------------------------------------------------------------- distances
def _static_dist_to_target():
    """Hop distance from every host to H5 on the full, intact network."""
    dist = {TARGET: 0}
    q = deque([TARGET])
    while q:
        u = q.popleft()
        for v in NEIGHBORS[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist

DIST_TO_TARGET = _static_dist_to_target()


def attack_cost_to_target(state: GameState) -> Optional[int]:
    """Cheapest number of attacker moves needed to compromise H5.

    Dijkstra over non-isolated hosts starting from every compromised,
    non-isolated host. Entering a clean unpatched host costs 1 move; a patched
    host costs 2 (it needs the one-shot zero-day) and is impassable once the
    zero-day is spent. Returns None if H5 cannot be reached.
    """
    INF = 10 ** 9
    best = [INF] * NUM_HOSTS
    heap = []
    for h in range(NUM_HOSTS):
        if state.compromised >> h & 1 and not state.isolated >> h & 1:
            best[h] = 0
            heap.append((0, h))
    heapq.heapify(heap)
    while heap:
        d, u = heapq.heappop(heap)
        if d > best[u]:
            continue
        if u == TARGET:
            return d
        for v in NEIGHBORS[u]:
            if state.isolated >> v & 1 or state.compromised >> v & 1:
                continue
            if state.patched >> v & 1:
                if state.zero_day_used:
                    continue
                w = 2
            else:
                w = 1
            if d + w < best[v]:
                best[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return None


# ---------------------------------------------------------------- evaluation
def evaluate(state: GameState) -> float:
    """Heuristic value (defender's perspective) of a non-terminal state.

    evaluate = utility(state) - threat
    utility : -(compromised value) - (defence cost spent) so far
    threat  : 100 / (d + 1), where d = attacker moves needed to compromise H5,
              counted only if the attacker still has enough moves left to
              compromise H5 *and* then play Exfiltrate (d + 1 moves).
    """
    base = utility(state)
    d = attack_cost_to_target(state)
    if d is None:
        return base
    attacker_moves_left = (MAX_PLIES - state.ply + 1) // 2 \
        if current_player(state) != DEFENDER else (MAX_PLIES - state.ply) // 2
    if d + 1 > attacker_moves_left:
        return base
    return base - 100.0 / (d + 1)


# ------------------------------------------------------------ action ordering
def naive_order(state: GameState, actions: List[Action]) -> List[Action]:
    """Keep the order produced by legal_actions (no domain knowledge)."""
    return actions


_KIND_RANK_ATT = {"Exfiltrate": 0, "Exploit": 1, "ZeroDay": 2, "Pass": 9}
_KIND_RANK_DEF = {"Restore": 0, "Isolate": 1, "Patch": 2, "Pass": 9}


def smart_order(state: GameState, actions: List[Action]) -> List[Action]:
    """Domain-knowledge ordering to improve alpha-beta cutoffs.

    Attacker: Exfiltrate first, then moves closest to H5 (cheapest exploit
              first, zero-day later), Pass last.
    Defender: moves touching hosts close to H5 / of high value first
              (protecting H5, H3, H7 ...), Pass last.
    """
    if current_player(state) == DEFENDER:
        def key(a):
            if a.kind == "Pass":
                return (9, 0, 0, 0)
            return (0, DIST_TO_TARGET[a.host], -ASSET_VALUE[a.host],
                    _KIND_RANK_DEF[a.kind])
    else:
        def key(a):
            if a.kind in ("Exfiltrate", "Pass"):
                return (_KIND_RANK_ATT[a.kind], 0, 0)
            return (1, DIST_TO_TARGET[a.host], _KIND_RANK_ATT[a.kind])
    return sorted(actions, key=key)


ORDERINGS = {"naive": naive_order, "smart": smart_order}


# ------------------------------------------------------------------- driver
def run_search(search_fn: Callable, algorithm: str, state: GameState,
               depth: Optional[int], ordering: str,
               measure_memory: bool = False) -> SearchResult:
    """Run `search_fn(state, depth, order, counter)` and collect statistics."""
    order = ORDERINGS[ordering]
    counter = Counter()
    if measure_memory:
        tracemalloc.start()
    t0 = time.perf_counter()
    value, move = search_fn(state, depth, order, counter)
    elapsed = time.perf_counter() - t0
    peak = None
    if measure_memory:
        peak = tracemalloc.get_traced_memory()[1] / 1024
        tracemalloc.stop()
    return SearchResult(algorithm, ordering, depth, move, value,
                        counter.expanded, counter.leaves, counter.pruned,
                        counter.max_depth, elapsed, peak)
