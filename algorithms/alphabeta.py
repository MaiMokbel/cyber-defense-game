"""Alpha-beta pruning. depth=None = full depth, depth=3 = depth-limited."""
from typing import Optional

from game.rules import (DEFENDER, apply_action, current_player, is_terminal,
                        legal_actions, utility)
from game.state import GameState

from .common import Counter, SearchResult, evaluate, run_search


def _alphabeta(state: GameState, depth_left: Optional[int], alpha: float,
               beta: float, order, c: Counter, level: int):
    c.max_depth = max(c.max_depth, level)
    if is_terminal(state):
        c.leaves += 1
        return utility(state), None
    if depth_left == 0:
        c.leaves += 1
        return evaluate(state), None

    c.expanded += 1
    nxt = None if depth_left is None else depth_left - 1
    actions = order(state, legal_actions(state))
    maximizing = current_player(state) == DEFENDER
    best_act = None

    if maximizing:
        best_val = float("-inf")
        for i, a in enumerate(actions):
            v, _ = _alphabeta(apply_action(state, a), nxt, alpha, beta,
                              order, c, level + 1)
            if v > best_val:
                best_val, best_act = v, a
            alpha = max(alpha, best_val)
            if alpha >= beta:                       # beta cutoff
                c.pruned += len(actions) - i - 1
                break
    else:
        best_val = float("inf")
        for i, a in enumerate(actions):
            v, _ = _alphabeta(apply_action(state, a), nxt, alpha, beta,
                              order, c, level + 1)
            if v < best_val:
                best_val, best_act = v, a
            beta = min(beta, best_val)
            if alpha >= beta:                       # alpha cutoff
                c.pruned += len(actions) - i - 1
                break
    return best_val, best_act


def alphabeta(state: GameState, depth: Optional[int] = None,
              ordering: str = "naive", measure_memory: bool = False
              ) -> SearchResult:
    name = "alphabeta" if depth is None else f"alphabeta-d{depth}"
    return run_search(
        lambda s, d, o, c: _alphabeta(s, d, float("-inf"), float("inf"),
                                      o, c, 0),
        name, state, depth, ordering, measure_memory)
