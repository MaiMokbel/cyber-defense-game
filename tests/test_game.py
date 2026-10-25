"""Task 1 tests: game model, legal moves, patching, winning, worked example."""
from dataclasses import replace

import pytest

from game.network import ASSET_VALUE, NEIGHBORS
from game.rules import (EXFILTRATE, PASS, Action, apply_action, current_player,
                        is_terminal, legal_actions, utility)
from game.state import hosts_in, initial_state


def play(*actions, state=None):
    state = state or initial_state()
    for a in actions:
        state = apply_action(state, a)
    return state


E = lambda h: Action("Exploit", h)
ZD = lambda h: Action("ZeroDay", h)
P = lambda h: Action("Patch", h)
I = lambda h: Action("Isolate", h)
R = lambda h: Action("Restore", h)


# ------------------------------------------------------------- network model
def test_network_is_symmetric_and_values_match_table():
    for a, ns in NEIGHBORS.items():
        for b in ns:
            assert a in NEIGHBORS[b]
    assert ASSET_VALUE[5] == 100 and ASSET_VALUE[0] == 0
    assert NEIGHBORS[5] == [3, 7]


# ------------------------------------------- TEST 1: legal moves
def test_legal_moves_at_start():
    s = initial_state()
    assert current_player(s) == "attacker"
    assert set(legal_actions(s)) == {E(1), E(2), PASS}

    # Defender (after Exploit(H1)): no Restore on clean hosts, H0 untouchable.
    s = play(E(1))
    acts = set(legal_actions(s))
    assert current_player(s) == "defender"
    assert P(3) in acts and I(3) in acts and R(1) in acts and PASS in acts
    assert R(3) not in acts                      # H3 is clean
    assert P(1) not in acts                      # H1 already compromised
    assert all(a.host != 0 for a in acts)        # H0 can never be targeted


def test_cannot_exploit_non_adjacent_host_and_illegal_raises():
    s = initial_state()
    assert E(5) not in legal_actions(s)
    with pytest.raises(ValueError):
        apply_action(s, E(5))


# ------------------------------------------- TEST 2: patching and zero-day
def test_patch_blocks_exploit_but_zero_day_works_once():
    s = play(E(1), P(3))
    assert s.spent == 2 and s.patched >> 3 & 1
    acts = legal_actions(s)
    assert E(3) not in acts and ZD(3) in acts    # patched -> only zero-day

    s = play(ZD(3), PASS, state=s)               # attacker breaks in, defender passes
    assert s.compromised >> 3 & 1 and s.zero_day_used
    # Patch another neighbour: zero-day is now gone for good.
    s = play(PASS, P(6), state=s)                # attacker passes, defender patches H6
    assert E(6) not in legal_actions(s) and ZD(6) not in legal_actions(s)


def test_zero_day_does_not_work_on_isolated_host():
    s = play(E(1), I(3))
    assert ZD(3) not in legal_actions(s) and E(3) not in legal_actions(s)


def test_isolated_compromised_host_cannot_spread():
    s = play(E(1), I(1))                         # H1 compromised, then isolated
    assert s.compromised >> 1 & 1                # still compromised (value counts)
    acts = legal_actions(s)
    assert E(3) not in acts and E(4) not in acts # H1's connections are gone
    assert E(2) in acts                          # H0 -> H2 is unaffected
    assert utility(s) == -10 - 8


def test_restore_cleans_and_patches():
    s = play(E(1), R(1))                         # cost 5
    assert not s.compromised >> 1 & 1 and s.patched >> 1 & 1
    assert s.spent == 5 and utility(s) == -5
    assert E(1) not in legal_actions(s)          # patched now
    assert ZD(1) in legal_actions(s)


def test_restore_does_not_undo_isolation():
    # Isolate (8) + Restore (5) exceeds the budget of 10 in real play, so this
    # state is built directly to check the rule itself.
    s = replace(initial_state(), compromised=0b11, isolated=0b10, ply=1)
    s = apply_action(s, R(1))
    assert not s.compromised >> 1 & 1
    assert s.patched >> 1 & 1 and s.isolated >> 1 & 1


# ------------------------------------------- TEST 3: winning (exfiltration)
def test_exfiltration_wins_and_ends_game():
    # H0 -> H1 -> H3 -> H5, defender passes throughout.
    s = play(E(1), PASS, E(3), PASS, E(5), PASS)
    assert not is_terminal(s)
    assert EXFILTRATE in legal_actions(s)
    s = apply_action(s, EXFILTRATE)
    assert s.exfiltrated and is_terminal(s)
    assert legal_actions(s) == []
    assert utility(s) == -(10 + 30 + 100) - 100   # = -240


def test_cannot_exfiltrate_from_isolated_database():
    s = replace(initial_state(), compromised=0b100001, isolated=0b100000)
    assert EXFILTRATE not in legal_actions(s)


# ------------------------------------------- worked example from the PDF
def test_worked_example_utility_is_minus_30():
    s = play(E(1), P(3), E(4), I(6))
    assert s.spent == 10 and s.ply == 4
    assert hosts_in(s.compromised) == [0, 1, 4]
    assert utility(s) == -30


# ------------------------------------------- budget and game length
def test_budget_limit():
    s = play(E(1), I(3), E(4))                   # 8 spent
    acts = legal_actions(s)
    assert P(6) in acts                          # 8 + 2 = 10 -> legal
    assert I(6) not in acts and R(1) not in acts and R(4) not in acts
    s = play(P(6), E(2), state=s)                # 10 spent
    assert s.spent == 10 and legal_actions(s) == [PASS]


def test_game_ends_after_10_plies():
    s = initial_state()
    for _ in range(10):
        assert not is_terminal(s)
        s = apply_action(s, PASS)
    assert s.ply == 10 and is_terminal(s) and legal_actions(s) == []
    assert utility(s) == 0


def test_state_is_immutable_and_hashable():
    s = initial_state()
    t = apply_action(s, E(1))
    assert s.compromised == 1                    # original untouched
    assert len({s, t, apply_action(s, E(1))}) == 2
