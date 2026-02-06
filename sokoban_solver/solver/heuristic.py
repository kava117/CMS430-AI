"""Heuristic functions for Sokoban A* search."""

from collections import deque


def manhattan_heuristic(boxes, goals):
    """Sum of minimum Manhattan distances from each box to nearest goal.

    Args:
        boxes: frozenset of (x, y) box positions.
        goals: frozenset of (x, y) goal positions.

    Returns:
        int: Lower bound on remaining pushes.
    """
    goal_list = list(goals)
    total = 0
    for bx, by in boxes:
        min_dist = min(abs(bx - gx) + abs(by - gy) for gx, gy in goal_list)
        total += min_dist
    return total


def precompute_goal_distances(walls, goals, width, height):
    """BFS from each goal to compute actual push distances to all reachable squares.

    Args:
        walls: frozenset of wall positions.
        goals: frozenset of goal positions.
        width: Grid width.
        height: Grid height.

    Returns:
        dict mapping (x, y, goal_idx) -> minimum distance.
    """
    distances = {}
    goal_list = list(goals)

    for goal_idx, goal_pos in enumerate(goal_list):
        queue = deque([(goal_pos, 0)])
        visited = {goal_pos}

        while queue:
            (x, y), dist = queue.popleft()
            distances[(x, y, goal_idx)] = dist

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < width and 0 <= ny < height and
                        (nx, ny) not in walls and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append(((nx, ny), dist + 1))

    return distances


def distance_heuristic(boxes, goals, goal_distances):
    """Sum of minimum precomputed distances from each box to nearest goal.

    Args:
        boxes: frozenset of (x, y) box positions.
        goals: frozenset of (x, y) goal positions.
        goal_distances: dict from precompute_goal_distances().

    Returns:
        int or float('inf') if any box can't reach any goal.
    """
    num_goals = len(goals)
    total = 0

    for bx, by in boxes:
        min_dist = float('inf')
        for goal_idx in range(num_goals):
            key = (bx, by, goal_idx)
            if key in goal_distances:
                min_dist = min(min_dist, goal_distances[key])

        if min_dist == float('inf'):
            return float('inf')
        total += min_dist

    return total
