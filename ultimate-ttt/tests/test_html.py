import unittest

class TestHTML(unittest.TestCase):
    def setUp(self):
        with open("templates/index.html") as f:
            self.html = f.read()

    def test_has_setup_panel(self):
        self.assertIn('id="setup-panel"', self.html)

    def test_has_game_panel(self):
        self.assertIn('id="game-panel"', self.html)

    def test_has_board_container(self):
        self.assertIn('id="board"', self.html)

    def test_has_status_bar(self):
        self.assertIn('id="status"', self.html)

    def test_loads_game_js(self):
        self.assertIn("game.js", self.html)

    def test_loads_style_css(self):
        self.assertIn("style.css", self.html)

    def test_difficulty_options(self):
        self.assertIn("easy", self.html.lower())
        self.assertIn("medium", self.html.lower())
        self.assertIn("hard", self.html.lower())

if __name__ == "__main__":
    unittest.main()
