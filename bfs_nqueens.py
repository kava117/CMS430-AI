"""
N-queens problem using breadth-first search

DSM and Claude, 2026
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


def solve_n_queens_bfs(n: int) -> tuple:
    """
    Solve the N-Queens problem using Breadth-First Search.
    
    Args:
        n: Size of the board (number of queens)
    
    Returns:
        A tuple representing a valid solution, or None if no solution exists
    """
    if n <= 0:
        return None, 0, 0

    # Track nodes expanded and created
    nodes_expanded = 0
    nodes_created = 0

    # Initialize empty frontier structure (queue for BFS)
    frontier = []

    # Begin with the starting state (empty board)
    initial_state = ()
    frontier.append(initial_state)
    nodes_created += 1

    while len(frontier) > 0:
        # Pop from the front of the queue
        x = frontier.pop(0)

        # If x is the goal state, we're done
        if is_goal(x, n):
            return x, nodes_expanded, nodes_created  # Output success

        # Generate successors of x
        nodes_expanded += 1
        s = get_successors(x, n)
        nodes_created += len(s)

        # Insert new unvisited successor states into frontier
        for i in s:
            frontier.append(i)

    # No solution was found
    return None, nodes_expanded, nodes_created


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
sizes = list(range(1, 10))
expanded_list = []
created_list = []

for n in sizes:
    solution, expanded, created = solve_n_queens_bfs(n)
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
plt.title("BFS N-Queens: Nodes Expanded vs Created")
plt.legend()
plt.savefig("bfs_nqueens_performance.png")
plt.close()
print("\nGraph saved to bfs_nqueens_performance.png")