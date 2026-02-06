from solver.heuristic import manhattan_heuristic, precompute_goal_distances, distance_heuristic


# --- Step 1.9: Manhattan heuristic tests ---

def test_heuristic_at_goal():
    boxes = frozenset([(2, 2)])
    goals = frozenset([(2, 2)])
    assert manhattan_heuristic(boxes, goals) == 0


def test_heuristic_one_away():
    boxes = frozenset([(2, 2)])
    goals = frozenset([(2, 3)])
    assert manhattan_heuristic(boxes, goals) == 1


def test_heuristic_multiple_boxes():
    boxes = frozenset([(1, 1), (3, 3)])
    goals = frozenset([(1, 2), (3, 4)])
    assert manhattan_heuristic(boxes, goals) == 2


def test_heuristic_picks_nearest_goal():
    boxes = frozenset([(2, 2)])
    goals = frozenset([(2, 3), (5, 5)])
    assert manhattan_heuristic(boxes, goals) == 1


# --- Step 1.12: Precomputed distance tests ---

def test_precompute_open_room():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                       (0, 1), (4, 1),
                       (0, 2), (4, 2),
                       (0, 3), (4, 3),
                       (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)])
    goals = frozenset([(2, 2)])

    distances = precompute_goal_distances(walls, goals, 5, 5)

    assert distances[(2, 2, 0)] == 0
    assert distances[(2, 1, 0)] == 1
    assert distances[(1, 2, 0)] == 1


def test_precompute_with_wall_obstacle():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                       (0, 1), (4, 1),
                       (0, 2), (2, 2), (4, 2),
                       (0, 3), (4, 3),
                       (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)])
    goals = frozenset([(1, 2)])

    distances = precompute_goal_distances(walls, goals, 5, 5)

    # (3,2) must go around the wall at (2,2)
    assert distances[(3, 2, 0)] == 4


def test_distance_heuristic_uses_precomputed():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0),
                       (0, 1), (3, 1),
                       (0, 2), (3, 2),
                       (0, 3), (1, 3), (2, 3), (3, 3)])
    goals = frozenset([(1, 1)])

    distances = precompute_goal_distances(walls, goals, 4, 4)
    boxes = frozenset([(2, 2)])

    h = distance_heuristic(boxes, goals, distances)
    assert h == 2


def test_distance_heuristic_unreachable():
    walls = frozenset([(0, 0), (1, 0), (2, 0),
                       (0, 1), (2, 1),
                       (0, 2), (1, 2), (2, 2),
                       (3, 0), (3, 1), (3, 2), (3, 3),
                       (4, 0), (4, 1), (4, 2), (4, 3)])
    goals = frozenset([(1, 1)])

    distances = precompute_goal_distances(walls, goals, 5, 4)
    # Box in completely disconnected area
    boxes = frozenset([(4, 3)])

    h = distance_heuristic(boxes, goals, distances)
    assert h == float('inf')
