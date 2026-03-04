import unittest
from game.state import GameState

class TestApplyMove(unittest.TestCase):
    def test_apply_move_does_not_mutate(self):
        gs = GameState()
        gs2 = gs.apply_move(0, 0)
        self.assertEqual(gs.board[0][0], 0)
        self.assertEqual(gs2.board[0][0], 1)

    def test_player_switches_after_move(self):
        gs = GameState()
        gs2 = gs.apply_move(0, 0)
        self.assertEqual(gs2.current_player, 2)

    def test_routing_sets_active_board(self):
        gs = GameState()
        gs2 = gs.apply_move(0, 4)
        self.assertEqual(gs2.active_board, 4)

    def test_routing_to_claimed_board_gives_free_choice(self):
        gs = GameState()
        gs.meta_board[4] = 1
        gs2 = gs.apply_move(0, 4)
        self.assertIsNone(gs2.active_board)

    def test_small_board_win_updates_meta(self):
        gs = GameState()
        gs.board[0] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 1
        gs.active_board = 0
        gs2 = gs.apply_move(0, 2)
        self.assertEqual(gs2.meta_board[0], 1)

    def test_small_board_draw_updates_meta(self):
        gs = GameState()
        gs.board[0] = [1,2,1, 2,1,2, 2,1,0]
        gs.current_player = 2
        gs.active_board = 0
        gs2 = gs.apply_move(0, 8)
        self.assertEqual(gs2.meta_board[0], 3)

    def test_game_not_terminal_after_one_move(self):
        gs = GameState()
        gs2 = gs.apply_move(4, 4)
        self.assertFalse(gs2.is_terminal())

    def test_meta_board_win_makes_terminal(self):
        gs = GameState()
        gs.meta_board = [1,1,0, 0,0,0, 0,0,0]
        gs.board[2] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 1
        gs.active_board = 2
        gs2 = gs.apply_move(2, 2)
        self.assertTrue(gs2.is_terminal())
        self.assertEqual(gs2.to_dict()["winner"], 1)

    def test_get_result_win(self):
        gs = GameState()
        gs.meta_board = [1,1,0, 0,0,0, 0,0,0]
        gs.board[2] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 1
        gs.active_board = 2
        gs2 = gs.apply_move(2, 2)
        self.assertEqual(gs2.get_result(1),  1.0)
        self.assertEqual(gs2.get_result(2), -1.0)

if __name__ == "__main__":
    unittest.main()
