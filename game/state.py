"""Immutable, hashable game state.

Host sets are stored as bitmasks (bit i = host Hi) so that states are tiny,
cheap to copy and usable as dictionary keys (e.g. transposition tables).
"""
from dataclasses import dataclass

from .network import ATTACKER_START

MAX_PLIES = 10
DEFENCE_BUDGET = 10


def bit(h: int) -> int:
    return 1 << h


def hosts_in(mask: int):
    """List of host ids whose bit is set in `mask`."""
    return [h for h in range(mask.bit_length()) if mask >> h & 1]


@dataclass(frozen=True, slots=True)
class GameState:
    compromised: int = bit(ATTACKER_START)   # H0 starts compromised
    patched: int = 0
    isolated: int = 0
    spent: int = 0                           # defence cost spent so far
    zero_day_used: bool = False
    ply: int = 0                             # plies played so far (0..10)
    exfiltrated: bool = False

    def __str__(self):
        return (f"ply={self.ply} compromised={hosts_in(self.compromised)} "
                f"patched={hosts_in(self.patched)} "
                f"isolated={hosts_in(self.isolated)} spent={self.spent} "
                f"zero_day_used={self.zero_day_used} "
                f"exfiltrated={self.exfiltrated}")


def initial_state() -> GameState:
    return GameState()
