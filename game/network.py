"""Static network description (hosts, asset values, connections)."""

NUM_HOSTS = 10
ATTACKER_START = 0   # H0 = Internet
TARGET = 5           # H5 = database (crown jewels)

HOST_NAMES = {
    0: "Internet",
    1: "Public web server",
    2: "Mail server",
    3: "App server",
    4: "Staff workstations",
    5: "Database",
    6: "Domain controller",
    7: "File server",
    8: "Backup server",
    9: "Admin laptop",
}

ASSET_VALUE = {0: 0, 1: 10, 2: 15, 3: 30, 4: 10,
               5: 100, 6: 60, 7: 25, 8: 20, 9: 40}

# Two-way connections, exactly as in the assignment table.
_EDGES = [
    (0, 1), (0, 2),
    (1, 3), (1, 4),
    (2, 4),
    (3, 5), (3, 6),
    (4, 6),
    (5, 7),
    (6, 7),
    (7, 8),
    (8, 9),
]

NEIGHBORS = {h: [] for h in range(NUM_HOSTS)}
for _a, _b in _EDGES:
    NEIGHBORS[_a].append(_b)
    NEIGHBORS[_b].append(_a)
for _h in NEIGHBORS:
    NEIGHBORS[_h].sort()

# Bitmask version of the adjacency, used for fast checks.
NEIGHBOR_MASK = {h: sum(1 << n for n in NEIGHBORS[h]) for h in NEIGHBORS}
