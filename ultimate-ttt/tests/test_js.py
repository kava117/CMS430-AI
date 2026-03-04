import unittest

class TestJS(unittest.TestCase):
    def setUp(self):
        with open("static/game.js") as f:
            self.js = f.read()

    def test_new_game_api_call(self):
        self.assertIn("/api/new_game", self.js)

    def test_move_api_call(self):
        self.assertIn("/api/move", self.js)

    def test_board_render_function(self):
        self.assertIn("renderBoard", self.js)

    def test_status_update(self):
        self.assertIn("status", self.js)

    def test_ai_flash_class(self):
        self.assertIn("ai-flash", self.js)

    def test_board_index_cell_index_sent(self):
        self.assertIn("board_index", self.js)
        self.assertIn("cell_index", self.js)

    def test_disable_on_waiting(self):
        self.assertTrue("disabled" in self.js or "waiting" in self.js
                        or "pointer-events" in self.js)

    def test_setup_panel_shown_on_game_end(self):
        self.assertIn("setup-panel", self.js)

if __name__ == "__main__":
    unittest.main()
