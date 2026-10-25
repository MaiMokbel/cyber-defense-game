"""Fixed initial states used by every algorithm in the experiments."""
from game.rules import Action, apply_action
from game.state import initial_state

E = lambda h: Action("Exploit", h)
P = lambda h: Action("Patch", h)
PASS = Action("Pass")


def _play(*actions):
    s = initial_state()
    for a in actions:
        s = apply_action(s, a)
    return s


# name -> (description, state)
EXPERIMENT_STATES = {
    "S0": ("Official start (attacker to move, 10 plies left)", _play()),
    "S1": ("After Exploit(H1) (defender to move)", _play(E(1))),
    "S2": ("Worked-example line: E(H1), Patch(H3), E(H4)",
           _play(E(1), P(3), E(4))),
    "S3": ("Attacker holds H3, next to the database (attacker to move)",
           _play(E(1), PASS, E(3), PASS)),
    "S4": ("Database H5 already compromised (defender to move)",
           _play(E(1), PASS, E(3), PASS, E(5))),
    "S5": ("Attacker via H2-H4-H6, 4 plies left (attacker to move)",
           _play(E(2), PASS, E(4), PASS, E(6), PASS)),
}
