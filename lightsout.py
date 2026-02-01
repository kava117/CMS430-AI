"""
Lights Out puzzle solver using BFS and Iterative Deepening
DSM and Claude, 2026
"""

from collections import deque
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def make_initial_state(n: int) -> tuple:
    """Return an n x n grid with all lights ON."""
    return tuple(tuple(True for _ in range(n)) for _ in range(n))


def press_button(state: tuple, row: int, col: int, n: int) -> tuple:
    """Toggle button at (row, col) and its neighbors."""
    # Convert to list of lists for mutation
    grid = [list(r) for r in state]

    # Toggle the button itself and its neighbors
    for dr, dc in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, c = row + dr, col + dc
        if 0 <= r < n and 0 <= c < n:
            grid[r][c] = not grid[r][c]

    return tuple(tuple(r) for r in grid)


def is_goal(state: tuple) -> bool:
    """Check if all lights are OFF."""
    return all(cell is False for row in state for cell in row)


def get_successors(state: tuple, n: int, pressed: set) -> list:
    """Generate valid successor states (unpressed buttons only)."""
    successors = []
    for row in range(n):
        for col in range(n):
            if (row, col) not in pressed:
                new_state = press_button(state, row, col, n)
                new_pressed = frozenset(pressed | {(row, col)})
                successors.append((new_state, (row, col), new_pressed))
    return successors


# ---------------------------------------------------------------------------
# Algorithm implementations
# ---------------------------------------------------------------------------

def solve_lights_out_bfs(n: int) -> tuple:
    """Solve using Breadth-First Search."""
    initial = make_initial_state(n)
    nodes_expanded = 0
    nodes_created = 0

    if is_goal(initial):
        return ((), nodes_expanded, nodes_created)

    queue = deque()
    queue.append((initial, frozenset(), ()))
    visited = {initial}

    while queue:
        state, pressed, path = queue.popleft()
        nodes_expanded += 1

        for new_state, button, new_pressed in get_successors(state, n, pressed):
            nodes_created += 1
            if new_state in visited:
                continue
            new_path = path + (button,)
            if is_goal(new_state):
                return (new_path, nodes_expanded, nodes_created)
            visited.add(new_state)
            queue.append((new_state, new_pressed, new_path))

    return (None, nodes_expanded, nodes_created)


def solve_lights_out_iddfs(n: int, max_depth: int = 20) -> tuple:
    """Solve using Iterative Deepening DFS."""
    initial = make_initial_state(n)
    total_expanded = 0
    total_created = 0

    for depth in range(max_depth + 1):
        solution, expanded, created = dfs_limited(initial, frozenset(), [], depth, 0, n)
        total_expanded += expanded
        total_created += created
        if solution is not None:
            return (solution, total_expanded, total_created)

    return (None, total_expanded, total_created)


def dfs_limited(state: tuple, pressed: set, path: list,
                depth_limit: int, current_depth: int, n: int) -> tuple:
    """Depth-limited DFS helper."""
    if is_goal(state):
        return (tuple(path), 0, 0)

    if current_depth >= depth_limit:
        return (None, 0, 0)

    expanded = 1
    created = 0
    for new_state, button, new_pressed in get_successors(state, n, pressed):
        created += 1
        solution, child_expanded, child_created = dfs_limited(
            new_state, new_pressed, path + [button],
            depth_limit, current_depth + 1, n
        )
        expanded += child_expanded
        created += child_created
        if solution is not None:
            return (solution, expanded, created)

    return (None, expanded, created)


# ---------------------------------------------------------------------------
# Performance analysis
# ---------------------------------------------------------------------------

def compare_algorithms(grid_sizes: list) -> dict:
    """Compare BFS vs IDDFS performance."""
    bfs_expanded = []
    bfs_created = []
    iddfs_expanded = []
    iddfs_created = []

    for n in grid_sizes:
        print(f"Testing {n}\u00d7{n} grid...")

        bfs_sol, bfs_exp, bfs_cre = solve_lights_out_bfs(n)
        bfs_len = len(bfs_sol) if bfs_sol else 0
        print(f"BFS: Solution found with {bfs_len} button presses, "
              f"{bfs_exp} nodes expanded, {bfs_cre} nodes created")

        iddfs_sol, iddfs_exp, iddfs_cre = solve_lights_out_iddfs(n)
        iddfs_len = len(iddfs_sol) if iddfs_sol else 0
        print(f"IDDFS: Solution found with {iddfs_len} button presses, "
              f"{iddfs_exp} nodes expanded, {iddfs_cre} nodes created")
        print()

        bfs_expanded.append(bfs_exp)
        bfs_created.append(bfs_cre)
        iddfs_expanded.append(iddfs_exp)
        iddfs_created.append(iddfs_cre)

    return {
        "grid_sizes": grid_sizes,
        "bfs_expanded": bfs_expanded,
        "bfs_created": bfs_created,
        "iddfs_expanded": iddfs_expanded,
        "iddfs_created": iddfs_created,
    }


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def print_grid(state: tuple) -> None:
    """Display grid state."""
    for row in state:
        print(" ".join("■" if cell else "□" for cell in row))


def print_solution(solution: tuple, n: int) -> None:
    """Display solution sequence."""
    state = make_initial_state(n)
    print("Initial state:")
    print_grid(state)
    print()
    for row, col in solution:
        state = press_button(state, row, col, n)
        print(f"Press button at ({row}, {col}):")
        print_grid(state)
        print()


def plot_performance(results: dict) -> None:
    """Create performance comparison graph."""
    sizes = results["grid_sizes"]
    plt.figure()
    plt.plot(sizes, results["bfs_expanded"], marker="o", label="BFS Expanded")
    plt.plot(sizes, results["bfs_created"], marker="o", linestyle="--", label="BFS Created")
    plt.plot(sizes, results["iddfs_expanded"], marker="s", label="IDDFS Expanded")
    plt.plot(sizes, results["iddfs_created"], marker="s", linestyle="--", label="IDDFS Created")
    plt.xlabel("Grid Size (N)")
    plt.ylabel("Nodes")
    plt.title("Nodes Expanded vs Nodes Created")
    plt.legend()
    plt.savefig("performance_comparison.png")
    plt.close()


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Test both algorithms on various grid sizes
    grid_sizes = [2, 3, 4]
    results = compare_algorithms(grid_sizes)

    # Generate performance graph
    plot_performance(results)

    # Example: Show solution for 3x3 grid
    solution, _, _ = solve_lights_out_bfs(3)
    print_solution(solution, 3)
