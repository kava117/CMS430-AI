"""Sokoban Solver - CLI Entry Point"""

import argparse
import sys
import time

from solver.astar import solve_puzzle
from core.parser import parse_puzzle_string, extract_elements
from core.state import State, PuzzleStatic
from visualization.terminal import display_state, playback_solution


def main():
    parser = argparse.ArgumentParser(
        description='Sokoban Puzzle Solver - finds optimal push solutions using A*'
    )
    parser.add_argument('puzzle_file', help='Path to puzzle file')
    parser.add_argument('-t', '--timeout', type=int, default=60,
                        help='Timeout in seconds (default: 60)')
    parser.add_argument('-m', '--max-states', type=int, default=10_000_000,
                        help='Maximum states to explore (default: 10000000)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--visualize', action='store_true',
                        help='Show solution playback in terminal')

    args = parser.parse_args()

    # Read puzzle file
    try:
        with open(args.puzzle_file, 'r') as f:
            puzzle_string = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.puzzle_file}' not found.")
        sys.exit(1)

    print(f"Puzzle: {args.puzzle_file}")
    if args.verbose:
        print(f"Puzzle contents:\n{puzzle_string}\n")

    # Solve
    result = solve_puzzle(puzzle_string, timeout=args.timeout, max_states=args.max_states)

    if result['success']:
        print(f"Solution found in {len(result['solution'])} pushes!\n")
        print(f"Solution: {result['solution']}\n")
        print("Statistics:")
        print(f"  States explored: {result['stats']['states_explored']:,}")
        print(f"  Time elapsed: {result['stats']['time_elapsed']:.2f} seconds")
        print(f"  Solution length: {len(result['solution'])} pushes")
        print(f"  Optimality: Guaranteed (A*)")

        if args.verbose:
            print("\nMove sequence:")
            for i, move in enumerate(result['solution']):
                names = {'U': 'Up', 'D': 'Down', 'L': 'Left', 'R': 'Right'}
                print(f"  {i + 1}. {move} ({names[move]})")

        if args.visualize:
            grid = parse_puzzle_string(puzzle_string)
            elements = extract_elements(grid)
            static = PuzzleStatic.from_elements(elements)
            initial = State(
                player_pos=elements['player'],
                boxes=frozenset(elements['boxes']),
            )
            print("\nPlayback:")
            playback_solution(initial, result['solution'], static, delay=0.3)
    else:
        print(f"No solution found.\n")
        print("Statistics:")
        stats = result.get('stats', {})
        if stats:
            print(f"  States explored: {stats.get('states_explored', 0):,}")
            print(f"  Time elapsed: {stats.get('time_elapsed', 0):.2f} seconds")
        print(f"  Termination reason: {result.get('reason', 'unknown')}")
        if result.get('error'):
            print(f"  Error: {result['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
