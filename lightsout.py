"""
N-queens problem using breadth-first search


DSM and Claude, 2026
"""


def flip_light(state, r: int, c: int, n) -> list:
    """
    Simulate a button click, invert all nearby lights
    """


    state[r][c] = not state[r][c] # initial button


    if c != 0:
        state[r][c-1] = not state[r][c-1] # up light
   
    if r != 0:
        state[r-1][c] = not state[r-1][c] # left light


    if r != n - 1:
        state[r+1][c] = not state[r+1][c] # right light


    if c != n - 1:
        state[r][c+1] = not state[r][c+1] # down light


    return state






def get_successors(state, n: int) -> list:
    """
    Generate all valid successor states by placing a queen in the next row.
    """


    successors = []
    ## row = len(state)  # Next row to place a queen
   
    ## if row >= n:
    ##     return successors
   
    for i in range(n):
        for j in range(n):
            print(f"getting successor for row {i} and col {j}")
            # use the flip light function to simulate the lights changing
            successors.append(flip_light(state, i, j, n))
   
    return successors




def is_goal(state, n: int) -> bool:
    for r in range(n):
        for c in range(n):
            if state[r][c] == False:
                return
    return True




def solve_lightsout_bfs(n: int) -> list:
    """
    Solve the N-Queens problem using Breadth-First Search.
   
    Args:
        n: Size of the board (number of queens)
   
    Returns:
        A tuple representing a valid solution, or None if no solution exists
    """
    if n <= 0:
        return None
   
    # Initialize empty frontier structure (queue for BFS)
    frontier = []
   
    # Begin with the starting state (empty board)
    initial_state = [[False for _ in range(n)] for _ in range(n)]
    frontier.append(initial_state)


    while len(frontier) > 0:
        # Pop from the front of the queue
        x = frontier.pop(0)
       
        # If x is the goal state, we're done
        if is_goal(x, n):
            return x  # Output success
       
        # Generate successors of x
        s = get_successors(x, n)
       
        # Insert new unvisited successor states into frontier
        for i in s:
            frontier.append(i)
   
    # No solution was found
    return None




def print_board(solution) -> None:
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
            if solution[row][col] == 0:
                line += " O |"
            else:
                line += " * |"
        print(line)
        print("+" + "---+" * n)




### Main
for n in range(1):
    solution = solve_lightsout_bfs(3)
    print_board(solution)