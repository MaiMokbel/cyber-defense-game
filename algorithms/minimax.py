"""Plain minimax (no pruning). depth=None searches to the end of the game;
an integer depth gives depth-limited minimax (see depth_limited.py)."""
from typing import Optional

from game.rules import (DEFENDER, apply_action, current_player, is_terminal,
                        legal_actions, utility)
from game.state import GameState

from .common import Counter, SearchResult, evaluate, run_search


def _minimax(state: GameState, depth_left: Optional[int], order, c: Counter,
             level: int):
    """Returns (value, best_action). Value is the defender's utility U."""
    c.max_depth = max(c.max_depth, level)
    if is_terminal(state):
        c.leaves += 1
        return utility(state), None
    if depth_left == 0:
        c.leaves += 1
        return evaluate(state), None

    c.expanded += 1
    nxt = None if depth_left is None else depth_left - 1
    maximizing = current_player(state) == DEFENDER
    best_val = float("-inf") if maximizing else float("inf")
    best_act = None
    for a in order(state, legal_actions(state)):
        v, _ = _minimax(apply_action(state, a), nxt, order, c, level + 1)
        if (maximizing and v > best_val) or (not maximizing and v < best_val):
            best_val, best_act = v, a
    return best_val, best_act


def minimax(state: GameState, depth: Optional[int] = None,
            ordering: str = "naive", measure_memory: bool = False
            ) -> SearchResult:
    """Full-depth minimax when depth is None, otherwise depth-limited."""
    name = "minimax" if depth is None else f"minimax-d{depth}"
    return run_search(
        lambda s, d, o, c: _minimax(s, d, o, c, 0),
        name, state, depth, ordering, measure_memory)
