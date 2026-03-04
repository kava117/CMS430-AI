import unittest
from game.state import GameState

class TestGameStateInit(unittest.TestCase):
    def test_initial_board_all_zeros(self):
        gs = GameState()
        for sub in gs.board:
            self.assertEqual(sub, [0]*9)

    def test_initial_meta_board_all_zeros(self):
        gs = GameState()
        self.assertEqual(gs.meta_board, [0]*9)

    def test_initial_current_player_is_x(self):
        gs = GameState()
        self.assertEqual(gs.current_player, 1)

    def test_initial_active_board_is_none(self):
        gs = GameState()
        self.assertIsNone(gs.active_board)

    def test_not_terminal_at_start(self):
        gs = GameState()
        self.assertFalse(gs.is_terminal())

    def test_clone_is_independent(self):
        gs = GameState()
        gs2 = gs.clone()
        gs2.board[0][0] = 1
        self.assertEqual(gs.board[0][0], 0)

    def test_clone_same_values(self):
        gs = GameState()
        gs2 = gs.clone()
        self.assertEqual(gs.board, gs2.board)
        self.assertEqual(gs.meta_board, gs2.meta_board)
        self.assertEqual(gs.current_player, gs2.current_player)
        self.assertIsNone(gs2.active_board)

    def test_to_dict_keys(self):
        gs = GameState()
        d = gs.to_dict()
        for key in ("board", "meta_board", "current_player", "active_board",
                    "is_terminal", "winner"):
            self.assertIn(key, d)

    def test_to_dict_winner_none_at_start(self):
        gs = GameState()
        d = gs.to_dict()
        self.assertIsNone(d["winner"])

    def test_to_dict_is_terminal_false_at_start(self):
        gs = GameState()
        d = gs.to_dict()
        self.assertFalse(d["is_terminal"])

if __name__ == "__main__":
    unittest.main()
