import math
import random


class MCTSNode:
    __slots__ = ("state", "parent", "children", "untried_moves",
                 "visit_count", "total_score", "move")

    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = {}          # move -> MCTSNode
        self.untried_moves = state.get_legal_moves()
        random.shuffle(self.untried_moves)
        self.visit_count = 0
        self.total_score = 0.0

    # ------------------------------------------------------------------
    # Node predicates
    # ------------------------------------------------------------------

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def is_terminal(self) -> bool:
        return self.state.is_terminal()

    # ------------------------------------------------------------------
    # UCB1
    # ------------------------------------------------------------------

    def ucb1(self, c: float = 1.414) -> float:
        if self.visit_count == 0:
            return math.inf
        exploitation = self.total_score / self.visit_count
        exploration = c * math.sqrt(
            math.log(self.parent.visit_count) / self.visit_count
        )
        return exploitation + exploration

    def best_child(self, c: float = 1.414) -> "MCTSNode":
        return max(self.children.values(), key=lambda n: n.ucb1(c))

    # ------------------------------------------------------------------
    # Tree growth
    # ------------------------------------------------------------------

    def expand(self) -> "MCTSNode":
        move = self.untried_moves.pop()
        child_state = self.state.apply_move(*move)
        child = MCTSNode(state=child_state, parent=self, move=move)
        self.children[move] = child
        return child


# ---------------------------------------------------------------------------
# MCTS
# ---------------------------------------------------------------------------

_DIFFICULTY = {
    "easy":   200,
    "medium": 1500,
    "hard":   10000,
}


class MCTS:
    def __init__(self, iterations: int):
        self.iterations = iterations

    def search(self, root_state) -> tuple:
        root = MCTSNode(state=root_state)

        for _ in range(self.iterations):
            node = self._select(root)
            if not node.is_terminal() and not node.is_fully_expanded():
                node = node.expand()
            result = self._rollout(node.state)
            self._backpropagate(node, result)

        # Pick child with most visits (exploitation)
        best = max(root.children.values(), key=lambda n: n.visit_count)
        return best.move

    # ------------------------------------------------------------------
    # Phases
    # ------------------------------------------------------------------

    def _select(self, node: MCTSNode) -> MCTSNode:
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.best_child(c=1.414)
        return node

    def _rollout(self, state) -> float:
        """Random playout; returns result from perspective of root player (player 1=X)."""
        current = state.clone()
        while not current.is_terminal():
            moves = current.get_legal_moves()
            move = random.choice(moves)
            current = current.apply_move(*move)
        # Return raw winner (1, 2, or 0); backprop interprets per-node
        return current._winner

    def _backpropagate(self, node: MCTSNode, winner: int):
        current = node
        while current is not None:
            current.visit_count += 1
            # The player who made the move to reach `current` is the parent's player
            if current.parent is not None:
                acting_player = current.parent.state.current_player
            else:
                acting_player = current.state.current_player
            if winner == 0:
                current.total_score += 0.5   # draw
            elif winner == acting_player:
                current.total_score += 1.0
            else:
                current.total_score += 0.0
            current = current.parent
