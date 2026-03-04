import unittest
from game.state import GameState

class TestTerminal(unittest.TestCase):
    def _make_terminal_draw(self):
        gs = GameState()
        gs.meta_board = [1,2,1, 2,2,1, 1,1,2]
        gs._terminal = True
        gs._winner = 0
        return gs

    def test_draw_is_terminal(self):
        gs = self._make_terminal_draw()
        self.assertTrue(gs.is_terminal())

    def test_draw_result_is_zero(self):
        gs = self._make_terminal_draw()
        self.assertEqual(gs.get_result(1), 0.0)
        self.assertEqual(gs.get_result(2), 0.0)

    def test_winner_dict_is_zero_on_draw(self):
        gs = self._make_terminal_draw()
        self.assertEqual(gs.to_dict()["winner"], 0)

    def test_get_result_raises_on_non_terminal(self):
        gs = GameState()
        with self.assertRaises(Exception):
            gs.get_result(1)

    def test_all_meta_resolved_no_winner_is_draw(self):
        gs = GameState()
        gs.meta_board = [1,2,1, 2,2,1, 1,1,2]
        gs._terminal = True
        gs._winner = 0
        self.assertTrue(gs.is_terminal())
        self.assertEqual(gs.get_result(1), 0.0)

if __name__ == "__main__":
    unittest.main()
