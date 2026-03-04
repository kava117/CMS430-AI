import unittest, math
from game.state import GameState
from game.mcts import MCTSNode

class TestMCTSNode(unittest.TestCase):
    def _root(self):
        return MCTSNode(state=GameState(), parent=None, move=None)

    def test_untried_moves_equals_legal_moves(self):
        node = self._root()
        self.assertEqual(len(node.untried_moves), 81)

    def test_not_fully_expanded_at_start(self):
        node = self._root()
        self.assertFalse(node.is_fully_expanded())

    def test_not_terminal_at_start(self):
        node = self._root()
        self.assertFalse(node.is_terminal())

    def test_ucb1_unvisited_is_inf(self):
        node = self._root()
        self.assertEqual(node.ucb1(), math.inf)

    def test_expand_reduces_untried_moves(self):
        node = self._root()
        node.expand()
        self.assertEqual(len(node.untried_moves), 80)

    def test_expand_adds_to_children(self):
        node = self._root()
        node.expand()
        self.assertEqual(len(node.children), 1)

    def test_expand_returns_mctsnode(self):
        node = self._root()
        child = node.expand()
        self.assertIsInstance(child, MCTSNode)

    def test_expand_child_has_correct_parent(self):
        node = self._root()
        child = node.expand()
        self.assertIs(child.parent, node)

    def test_fully_expanded_after_all_moves(self):
        node = self._root()
        for _ in range(81):
            node.expand()
        self.assertTrue(node.is_fully_expanded())

    def test_ucb1_value_computed(self):
        node = self._root()
        node.visit_count = 10
        node.total_score = 5.0
        child = node.expand()
        child.visit_count = 2
        child.total_score = 1.0
        val = child.ucb1(c=1.414)
        expected = 1.0/2.0 + 1.414 * math.sqrt(math.log(10) / 2)
        self.assertAlmostEqual(val, expected, places=5)

    def test_best_child_returns_highest_ucb1(self):
        node = self._root()
        node.visit_count = 10
        c1 = node.expand()
        c1.visit_count = 1
        c1.total_score = 0.0
        c2 = node.expand()
        c2.visit_count = 1
        c2.total_score = 1.0
        best = node.best_child(c=0.0)
        self.assertIs(best, c2)

if __name__ == "__main__":
    unittest.main()
