"""Task 2 tests: minimax, depth-limited minimax and alpha-beta."""
import pytest

from algorithms.alphabeta import alphabeta
from algorithms.common import attack_cost_to_target, evaluate
from algorithms.depth_limited import DEFAULT_DEPTH, depth_limited_minimax
from algorithms.minimax import minimax
from experiments.states import EXPERIMENT_STATES
from game.rules import Action, apply_action, is_terminal, legal_actions
from game.state import initial_state

# States whose full-depth minimax is cheap enough for a unit test.
CHEAP = ["S2", "S3", "S4", "S5"]


def state(name):
    return EXPERIMENT_STATES[name][1]


@pytest.mark.parametrize("name", CHEAP)
@pytest.mark.parametrize("ordering", ["naive", "smart"])
def test_alphabeta_equals_minimax_full_depth(name, ordering):
    mm = minimax(state(name), None, ordering)
    ab = alphabeta(state(name), None, ordering)
    assert ab.value == mm.value          # optimality is preserved
    assert ab.move == mm.move            # same tie-breaking
    assert ab.visited < mm.visited       # but far fewer nodes
    assert ab.pruned > 0


def test_alphabeta_equals_minimax_depth_limited_from_start():
    for depth in (3, 5, 6):
        mm = minimax(initial_state(), depth, "naive")
        ab = alphabeta(initial_state(), depth, "naive")
        assert (ab.value, ab.move) == (mm.value, mm.move)


def test_move_ordering_does_not_change_value():
    naive = alphabeta(state("S2"), None, "naive")
    smart = alphabeta(state("S2"), None, "smart")
    assert naive.value == smart.value


def test_known_optimal_value_from_start():
    # Verified against full minimax (48 s), see results/summary.md.
    assert alphabeta(initial_state(), None, "naive").value == -44


def test_depth_limited_default_depth_is_three():
    res = depth_limited_minimax(initial_state())
    assert res.depth == DEFAULT_DEPTH == 3
    assert res.max_depth <= 3
    assert res.move in legal_actions(initial_state())


def test_returned_move_is_always_legal():
    for name in EXPERIMENT_STATES:
        for algo in (minimax, alphabeta):
            res = algo(state(name), 3, "smart")
            assert res.move in legal_actions(state(name))


def test_terminal_state_has_no_move():
    s = initial_state()
    for _ in range(10):
        s = apply_action(s, Action("Pass"))
    res = alphabeta(s, 3)
    assert is_terminal(s) and res.move is None and res.value == 0


def test_attacker_exfiltrates_when_possible():
    # S4: H5 is compromised and it is the defender's turn; if the defender
    # passes, the attacker should exfiltrate immediately.
    s = apply_action(state("S4"), Action("Pass"))
    for algo in (minimax, alphabeta):
        assert algo(s, 3).move == Action("Exfiltrate")


def test_defender_stops_exfiltration_when_database_compromised():
    # In S4 the attacker threatens Exfiltrate; the defender must act on H5.
    for algo in (minimax, alphabeta):
        res = algo(state("S4"), 3, "smart")
        assert res.move.host == 5 and res.move.kind in ("Restore", "Isolate")


def test_evaluation_heuristic_is_sensible():
    s0 = initial_state()
    s_close = state("S3")                       # attacker next to H5
    assert attack_cost_to_target(s0) == 3       # H0-H1-H3-H5
    assert attack_cost_to_target(s_close) == 1
    assert evaluate(s_close) < evaluate(s0) - 30


def test_statistics_are_recorded():
    res = alphabeta(initial_state(), 3, "naive", measure_memory=True)
    assert res.expanded > 0 and res.leaves > 0 and res.time_s > 0
    assert res.peak_mem_kb is not None
