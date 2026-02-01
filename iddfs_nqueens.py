"""
N-queens problem using iterative deepening depth-first search

DSM and Claude, 2026
(I fixed the range issue in main, but kept the original code intact beyond that)
"""

import matplotlib.pyplot as plt


def is_safe(state: tuple, row: int, col: int) -> bool:
    """
    Check if placing a queen at (row, col) is safe given the current state.

    Args:
        state: Current partial solution (tuple of column positions)
        row: Row to place the new queen
        col: Column to place the new queen

    Returns:
        True if placement is safe, False otherwise
    """

    # The built-in enumerate function generates (index, value) pairs for the items
    # in the tuple
    for r, c in enumerate(state):

        # Check column conflict (row conflict is impossible by construction)
        if c == col:
            return False

        # Check diagonal conflict
        if abs(r - row) == abs(c - col):
            return False

    # No conflict was found, so this placement is valid
    return True


def get_successors(state: tuple, n: int) -> list:
    """
    Generate all valid successor states by placing a queen in the next row.
    """

    successors = []
    row = len(state)  # Next row to place a queen

    if row >= n:
        return successors

    for col in range(n):

        # If (row, col) is a safe position, create a successor by appending
        # col to the current state tuple
        if is_safe(state, row, col):
            successors.append(state + (col,))

    return successors


def is_goal(state: tuple, n: int) -> bool:
    return len(state) == n


def dfs_limited(state: tuple, n: int, depth_limit: int) -> tuple:
    """
    Depth-limited DFS helper for IDDFS.

    Args:
        state: Current partial solution (tuple of column positions)
        n: Size of the board
        depth_limit: Maximum depth to search

    Returns:
        (solution, nodes_expanded, nodes_created)
    """
    # Current depth is the number of queens placed so far
    current_depth = len(state)

    nodes_expanded = 0
    nodes_created = 0

    # If this state is the goal, return it
    if is_goal(state, n):
        return state, nodes_expanded, nodes_created

    # If we've reached the depth limit, stop expanding
    if current_depth >= depth_limit:
        return None, nodes_expanded, nodes_created

    # Generate successors and recurse
    nodes_expanded += 1
    successors = get_successors(state, n)
    nodes_created += len(successors)

    for successor in successors:
        result, child_expanded, child_created = dfs_limited(successor, n, depth_limit)
        nodes_expanded += child_expanded
        nodes_created += child_created
        if result is not None:
            return result, nodes_expanded, nodes_created

    # No solution found in this branch
    return None, nodes_expanded, nodes_created


def solve_n_queens_iddfs(n: int) -> tuple:
    """
    Solve the N-Queens problem using Iterative Deepening Depth-First Search.

    Progressively increases the depth limit from 0 to n, running a
    depth-limited DFS at each iteration.

    Args:
        n: Size of the board (number of queens)

    Returns:
        A tuple representing a valid solution, or None if no solution exists
    """
    if n <= 0:
        return None, 0, 0

    # Track totals across all depth iterations
    total_expanded = 0
    total_created = 0

    # Begin with the starting state (empty board)
    initial_state = ()

    # Iteratively deepen from depth 0 to n
    for depth_limit in range(n + 1):
        result, expanded, created = dfs_limited(initial_state, n, depth_limit)
        total_expanded += expanded
        total_created += created
        if result is not None:
            return result, total_expanded, total_created

    # No solution was found
    return None, total_expanded, total_created


def print_board(solution: tuple) -> None:
    """
    Print the chessboard with queens placed.
    """
    if solution is None:
        print("No solution found")
        return

    n = len(solution)
    print(f"\n{n}-Queens Solution:")
    print("+" + "---+" * n)

    for row in range(n):
        line = "|"
        for col in range(n):
            if solution[row] == col:
                line += " Q |"
            else:
                line += "   |"
        print(line)
        print("+" + "---+" * n)


### Main
sizes = list(range(1, 13))
expanded_list = []
created_list = []

for n in sizes:
    solution, expanded, created = solve_n_queens_iddfs(n)
    expanded_list.append(expanded)
    created_list.append(created)
    print_board(solution)
    print(f"Nodes expanded: {expanded}, Nodes created: {created}")

# Plot nodes expanded vs created as a function of n
plt.figure()
plt.plot(sizes, expanded_list, marker="o", label="Nodes Expanded")
plt.plot(sizes, created_list, marker="s", linestyle="--", label="Nodes Created")
plt.xlabel("Board Size (N)")
plt.ylabel("Nodes")
plt.title("IDDFS N-Queens: Nodes Expanded vs Created")
plt.legend()
plt.savefig("iddfs_nqueens_performance.png")
plt.close()
print("\nGraph saved to iddfs_nqueens_performance.png")
