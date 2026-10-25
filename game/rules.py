"""Game rules: legal actions, transitions, terminal test and utility."""
from typing import List, NamedTuple

from .network import (ASSET_VALUE, ATTACKER_START, NEIGHBOR_MASK, NUM_HOSTS,
                      TARGET)
from .state import DEFENCE_BUDGET, MAX_PLIES, GameState, bit, hosts_in

ATTACKER = "attacker"
DEFENDER = "defender"

COST = {"Patch": 2, "Isolate": 8, "Restore": 5, "Pass": 0}


class Action(NamedTuple):
    kind: str            # Exploit, ZeroDay, Exfiltrate, Patch, Isolate, Restore, Pass
    host: int = -1       # target host (-1 when not applicable)

    def __str__(self):
        return self.kind if self.host < 0 else f"{self.kind}(H{self.host})"


PASS = Action("Pass")
EXFILTRATE = Action("Exfiltrate")


# ----------------------------------------------------------------- helpers
def current_player(state: GameState) -> str:
    """Attacker moves on even plies (0, 2, ...), defender on odd plies."""
    return ATTACKER if state.ply % 2 == 0 else DEFENDER


def is_terminal(state: GameState) -> bool:
    return state.exfiltrated or state.ply >= MAX_PLIES


def _active_source(state: GameState, h: int) -> bool:
    """True if h has an active connection to a compromised, non-isolated host."""
    if state.isolated >> h & 1:
        return False
    sources = state.compromised & ~state.isolated
    return bool(NEIGHBOR_MASK[h] & sources)


# ----------------------------------------------------------- legal actions
def _attacker_actions(state: GameState) -> List[Action]:
    actions = []
    for h in range(NUM_HOSTS):
        if h == ATTACKER_START or state.compromised >> h & 1:
            continue                         # must be clean
        if not _active_source(state, h):     # also covers "not isolated"
            continue
        if not state.patched >> h & 1:
            actions.append(Action("Exploit", h))
        elif not state.zero_day_used:
            actions.append(Action("ZeroDay", h))
    if state.compromised >> TARGET & 1 and not state.isolated >> TARGET & 1:
        actions.append(EXFILTRATE)
    actions.append(PASS)
    return actions


def _defender_actions(state: GameState) -> List[Action]:
    left = DEFENCE_BUDGET - state.spent
    actions = []
    for h in range(NUM_HOSTS):
        if h == ATTACKER_START:              # H0 can never be touched
            continue
        compromised = state.compromised >> h & 1
        if (not compromised and not state.patched >> h & 1
                and COST["Patch"] <= left):
            actions.append(Action("Patch", h))
        if not state.isolated >> h & 1 and COST["Isolate"] <= left:
            actions.append(Action("Isolate", h))
        if compromised and COST["Restore"] <= left:
            actions.append(Action("Restore", h))
    actions.append(PASS)
    return actions


def legal_actions(state: GameState) -> List[Action]:
    """Legal actions for the player to move (empty if the game is over)."""
    if is_terminal(state):
        return []
    if current_player(state) == ATTACKER:
        return _attacker_actions(state)
    return _defender_actions(state)


# -------------------------------------------------------------- transition
def apply_action(state: GameState, action: Action) -> GameState:
    """Return the new state after `action`. Raises ValueError if illegal."""
    if action not in legal_actions(state):
        raise ValueError(f"Illegal action {action} in state: {state}")

    comp, pat, iso = state.compromised, state.patched, state.isolated
    spent, zd, exf = state.spent, state.zero_day_used, state.exfiltrated
    kind, h = action

    if kind == "Exploit":
        comp |= bit(h)
    elif kind == "ZeroDay":
        comp |= bit(h)
        zd = True
    elif kind == "Exfiltrate":
        exf = True
    elif kind == "Patch":
        pat |= bit(h)
        spent += COST["Patch"]
    elif kind == "Isolate":
        iso |= bit(h)
        spent += COST["Isolate"]
    elif kind == "Restore":
        comp &= ~bit(h)
        pat |= bit(h)
        spent += COST["Restore"]
    # "Pass": nothing changes except the ply counter.

    return GameState(comp, pat, iso, spent, zd, state.ply + 1, exf)


# ----------------------------------------------------------------- utility
def compromised_value(state: GameState) -> int:
    return sum(ASSET_VALUE[h] for h in hosts_in(state.compromised))


def utility(state: GameState) -> int:
    """Defender's utility U (attacker's utility is -U).

    U = -(value of compromised hosts) - (defence cost spent) - 100*I
    Also used as the 'current score' of any non-terminal state.
    """
    return (-compromised_value(state) - state.spent
            - (100 if state.exfiltrated else 0))
