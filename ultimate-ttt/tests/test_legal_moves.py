import unittest
from game.state import GameState

class TestLegalMoves(unittest.TestCase):
    def test_initial_state_has_81_moves(self):
        gs = GameState()
        moves = gs.get_legal_moves()
        self.assertEqual(len(moves), 81)

    def test_initial_moves_span_all_boards(self):
        gs = GameState()
        boards = {b for b, _ in gs.get_legal_moves()}
        self.assertEqual(boards, set(range(9)))

    def test_active_board_restricts_moves(self):
        gs = GameState()
        gs.active_board = 4
        moves = gs.get_legal_moves()
        self.assertTrue(all(b == 4 for b, _ in moves))
        self.assertEqual(len(moves), 9)

    def test_one_cell_filled_in_active_board(self):
        gs = GameState()
        gs.active_board = 0
        gs.board[0][0] = 1
        moves = gs.get_legal_moves()
        self.assertEqual(len(moves), 8)
        self.assertNotIn((0, 0), moves)

    def test_claimed_board_excluded_from_free_choice(self):
        gs = GameState()
        gs.active_board = None
        gs.meta_board[3] = 1
        moves = gs.get_legal_moves()
        self.assertTrue(all(b != 3 for b, _ in moves))
        self.assertEqual(len(moves), 72)

    def test_active_board_claimed_gives_free_choice(self):
        gs = GameState()
        gs.active_board = 3
        gs.meta_board[3] = 1
        moves = gs.get_legal_moves()
        boards = {b for b, _ in moves}
        self.assertNotIn(3, boards)
        self.assertEqual(len(moves), 72)

    def test_terminal_state_returns_empty(self):
        gs = GameState()
        gs._terminal = True
        self.assertEqual(gs.get_legal_moves(), [])

if __name__ == "__main__":
    unittest.main()
