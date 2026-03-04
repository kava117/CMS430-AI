import unittest
from game.state import GameState
from game.mcts import MCTS

class TestMCTSSearch(unittest.TestCase):
    def test_search_returns_tuple(self):
        gs = GameState()
        mcts = MCTS(iterations=50)
        move = mcts.search(gs)
        self.assertIsInstance(move, tuple)
        self.assertEqual(len(move), 2)

    def test_search_returns_legal_move(self):
        gs = GameState()
        mcts = MCTS(iterations=50)
        move = mcts.search(gs)
        self.assertIn(move, gs.get_legal_moves())

    def test_search_respects_active_board(self):
        gs = GameState()
        gs.active_board = 3
        mcts = MCTS(iterations=50)
        board_idx, _ = mcts.search(gs)
        self.assertEqual(board_idx, 3)

    def test_search_takes_winning_move(self):
        """MCTS with enough iterations should take an obvious win."""
        gs = GameState()
        gs.meta_board = [1,1,0, 0,0,0, 0,0,0]
        gs.board[2] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 1
        gs.active_board = 2
        mcts = MCTS(iterations=500)
        move = mcts.search(gs)
        self.assertEqual(move, (2, 2))

    def test_search_blocks_opponent_win(self):
        """MCTS should not let O win the meta-board immediately."""
        gs = GameState()
        gs.meta_board = [2,2,0, 0,0,0, 0,0,0]
        gs.board[2] = [2,2,0, 0,0,0, 0,0,0]
        gs.current_player = 1
        gs.active_board = 2
        mcts = MCTS(iterations=500)
        move = mcts.search(gs)
        # After X moves, O must not be able to immediately win the meta-board
        next_state = gs.apply_move(*move)
        for o_move in next_state.get_legal_moves():
            after_o = next_state.apply_move(*o_move)
            self.assertNotEqual(after_o.to_dict()["winner"], 2,
                msg=f"X played {move}, O can immediately win meta with {o_move}")

    def test_search_on_near_terminal_state(self):
        """search on a state one move from terminal should not crash."""
        gs = GameState()
        gs.meta_board = [1,1,0, 0,0,0, 0,0,0]
        gs.board[2] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 2
        gs.active_board = 2
        mcts = MCTS(iterations=100)
        move = mcts.search(gs)
        self.assertIn(move, gs.get_legal_moves())

if __name__ == "__main__":
    unittest.main()
