import unittest, os

class TestScaffold(unittest.TestCase):
    def test_game_package_importable(self):
        import game
    def test_state_module_importable(self):
        import game.state
    def test_mcts_module_importable(self):
        import game.mcts
    def test_requirements_file_exists(self):
        self.assertTrue(os.path.exists("requirements.txt"))
    def test_templates_dir_exists(self):
        self.assertTrue(os.path.isdir("templates"))
    def test_static_dir_exists(self):
        self.assertTrue(os.path.isdir("static"))

if __name__ == "__main__":
    unittest.main()
