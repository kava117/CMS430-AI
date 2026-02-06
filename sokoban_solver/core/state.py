"""State representation for Sokoban solver."""


class State:
    """Dynamic state during A* search.

    Attributes:
        player_pos: (x, y) tuple of player position.
        boxes: frozenset of (x, y) tuples for box positions.
    """

    __slots__ = ('player_pos', 'boxes')

    def __init__(self, player_pos, boxes):
        self.player_pos = player_pos
        self.boxes = boxes if isinstance(boxes, frozenset) else frozenset(boxes)

    def __hash__(self):
        return hash((self.player_pos, self.boxes))

    def __eq__(self, other):
        return (self.player_pos == other.player_pos and
                self.boxes == other.boxes)

    def __repr__(self):
        return f"State(player={self.player_pos}, boxes={self.boxes})"


class PuzzleStatic:
    """Static puzzle data computed once at load time.

    Attributes:
        walls: frozenset of (x, y) wall positions.
        goals: frozenset of (x, y) goal positions.
        width: Grid width.
        height: Grid height.
        deadlock_squares: frozenset of positions where a box is always stuck.
    """

    def __init__(self, walls, goals, width, height, deadlock_squares=None):
        self.walls = walls if isinstance(walls, frozenset) else frozenset(walls)
        self.goals = goals if isinstance(goals, frozenset) else frozenset(goals)
        self.width = width
        self.height = height
        self.deadlock_squares = deadlock_squares or frozenset()

    @classmethod
    def from_elements(cls, elements):
        """Create PuzzleStatic from extract_elements() output."""
        return cls(
            walls=frozenset(elements['walls']),
            goals=frozenset(elements['goals']),
            width=elements['width'],
            height=elements['height'],
        )


def is_goal_state(state, puzzle_static):
    """Check if all boxes are on goal positions."""
    return state.boxes == puzzle_static.goals
