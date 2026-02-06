"""A* search solver for Sokoban puzzles."""

import heapq
import time

from core.parser import parse_puzzle_string, extract_elements
from core.state import State, PuzzleStatic, is_goal_state
from core.moves import generate_moves
from solver.heuristic import precompute_goal_distances, distance_heuristic


def solve(initial_state, puzzle_static, timeout=60, max_states=10_000_000):
    """Solve a Sokoban puzzle using A* search.

    Args:
        initial_state: Starting State.
        puzzle_static: PuzzleStatic with precomputed data.
        timeout: Max seconds before giving up.
        max_states: Max states to explore.

    Returns:
        dict with 'success', 'solution', 'stats', etc.
    """
    start_time = time.time()

    # Precompute goal distances for heuristic
    goal_distances = precompute_goal_distances(
        puzzle_static.walls, puzzle_static.goals,
        puzzle_static.width, puzzle_static.height
    )

    # Check if already solved
    if is_goal_state(initial_state, puzzle_static):
        return {
            'success': True,
            'solution': '',
            'stats': {
                'states_explored': 0,
                'time_elapsed': time.time() - start_time,
                'optimal': True,
            },
        }

    # Priority queue: (f_score, counter, g_score, state, path)
    counter = 0
    h = distance_heuristic(initial_state.boxes, puzzle_static.goals, goal_distances)
    if h == float('inf'):
        return {
            'success': False,
            'error': 'No solution found',
            'reason': 'unsolvable',
            'stats': {
                'states_explored': 0,
                'time_elapsed': time.time() - start_time,
            },
        }

    open_set = [(h, counter, 0, initial_state, '')]
    closed_set = set()
    # Track best g-score for each state
    best_g = {initial_state: 0}
    states_explored = 0

    while open_set:
        # Check timeout
        elapsed = time.time() - start_time
        if elapsed > timeout:
            return {
                'success': False,
                'error': 'Search terminated: timeout reached',
                'reason': 'timeout',
                'stats': {
                    'states_explored': states_explored,
                    'time_elapsed': elapsed,
                },
            }

        if states_explored >= max_states:
            return {
                'success': False,
                'error': 'Search terminated: max states reached',
                'reason': 'timeout',
                'stats': {
                    'states_explored': states_explored,
                    'time_elapsed': time.time() - start_time,
                },
            }

        f, _, g, current_state, path = heapq.heappop(open_set)

        # Skip if we already found a better path to this state
        if current_state in closed_set:
            continue

        closed_set.add(current_state)
        states_explored += 1

        # Generate successor states
        moves = generate_moves(current_state, puzzle_static)

        for direction, new_state in moves:
            if new_state in closed_set:
                continue

            # Check deadlock squares
            if any(box in puzzle_static.deadlock_squares for box in new_state.boxes):
                continue

            new_g = g + 1
            new_path = path + direction

            # Check if goal
            if is_goal_state(new_state, puzzle_static):
                return {
                    'success': True,
                    'solution': new_path,
                    'stats': {
                        'states_explored': states_explored,
                        'time_elapsed': time.time() - start_time,
                        'optimal': True,
                    },
                }

            # Only add if this is a better path
            if new_state not in best_g or new_g < best_g[new_state]:
                best_g[new_state] = new_g
                new_h = distance_heuristic(new_state.boxes, puzzle_static.goals, goal_distances)
                if new_h < float('inf'):
                    counter += 1
                    heapq.heappush(open_set, (new_g + new_h, counter, new_g, new_state, new_path))

    return {
        'success': False,
        'error': 'No solution exists',
        'reason': 'unsolvable',
        'stats': {
            'states_explored': states_explored,
            'time_elapsed': time.time() - start_time,
        },
    }


def solve_puzzle(puzzle_string, timeout=60, max_states=10_000_000):
    """High-level API: solve a puzzle from its string representation.

    Args:
        puzzle_string: Standard Sokoban text format.
        timeout: Max seconds.
        max_states: Max states to explore.

    Returns:
        dict with 'success', 'solution', 'stats', 'initial_state', 'error', 'reason'.
    """
    try:
        grid = parse_puzzle_string(puzzle_string)
        if not grid:
            return {
                'success': False,
                'error': 'Empty puzzle',
                'reason': 'invalid_puzzle',
            }

        elements = extract_elements(grid)

        if elements['player'] is None:
            return {
                'success': False,
                'error': 'No player found in puzzle',
                'reason': 'invalid_puzzle',
            }

        if not elements['boxes']:
            return {
                'success': False,
                'error': 'No boxes found in puzzle',
                'reason': 'invalid_puzzle',
            }

        if not elements['goals']:
            return {
                'success': False,
                'error': 'No goals found in puzzle',
                'reason': 'invalid_puzzle',
            }

        if len(elements['boxes']) != len(elements['goals']):
            return {
                'success': False,
                'error': f"Box count ({len(elements['boxes'])}) != goal count ({len(elements['goals'])})",
                'reason': 'invalid_puzzle',
            }

        static = PuzzleStatic.from_elements(elements)

        # Compute deadlock squares (import here to avoid circular imports at module level)
        from solver.deadlock import compute_static_deadlocks
        static.deadlock_squares = compute_static_deadlocks(
            static.walls, static.goals, static.width, static.height
        )

        initial = State(
            player_pos=elements['player'],
            boxes=frozenset(elements['boxes']),
        )

        result = solve(initial, static, timeout=timeout, max_states=max_states)

        # Add initial_state info for the API
        result['initial_state'] = {
            'player': list(elements['player']),
            'boxes': [list(b) for b in elements['boxes']],
            'goals': [list(g) for g in elements['goals']],
        }

        return result

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'reason': 'invalid_puzzle',
        }
