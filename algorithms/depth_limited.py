"""Depth-limited minimax (default depth = 3 plies, as required)."""
from game.state import GameState

from .common import SearchResult
from .minimax import minimax

DEFAULT_DEPTH = 3


def depth_limited_minimax(state: GameState, depth: int = DEFAULT_DEPTH,
                          ordering: str = "naive",
                          measure_memory: bool = False) -> SearchResult:
    return minimax(state, depth, ordering, measure_memory)
