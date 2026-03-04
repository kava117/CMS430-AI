import unittest
from game.state import check_winner

class TestCheckWinner(unittest.TestCase):
    def test_no_winner_empty(self):
        self.assertEqual(check_winner([0]*9), 0)

    def test_x_wins_top_row(self):
        self.assertEqual(check_winner([1,1,1, 0,0,0, 0,0,0]), 1)

    def test_x_wins_middle_row(self):
        self.assertEqual(check_winner([0,0,0, 1,1,1, 0,0,0]), 1)

    def test_x_wins_bottom_row(self):
        self.assertEqual(check_winner([0,0,0, 0,0,0, 1,1,1]), 1)

    def test_o_wins_left_col(self):
        self.assertEqual(check_winner([2,0,0, 2,0,0, 2,0,0]), 2)

    def test_o_wins_middle_col(self):
        self.assertEqual(check_winner([0,2,0, 0,2,0, 0,2,0]), 2)

    def test_o_wins_right_col(self):
        self.assertEqual(check_winner([0,0,2, 0,0,2, 0,0,2]), 2)

    def test_x_wins_main_diagonal(self):
        self.assertEqual(check_winner([1,0,0, 0,1,0, 0,0,1]), 1)

    def test_x_wins_anti_diagonal(self):
        self.assertEqual(check_winner([0,0,1, 0,1,0, 1,0,0]), 1)

    def test_o_wins_anti_diagonal(self):
        self.assertEqual(check_winner([0,0,2, 0,2,0, 2,0,0]), 2)

    def test_no_winner_partial(self):
        self.assertEqual(check_winner([1,2,1, 2,1,2, 0,0,0]), 0)

    def test_no_winner_full_draw(self):
        self.assertEqual(check_winner([1,2,1, 2,2,1, 1,1,2]), 0)

if __name__ == "__main__":
    unittest.main()
