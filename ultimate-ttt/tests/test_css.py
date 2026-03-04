import unittest

class TestCSS(unittest.TestCase):
    def setUp(self):
        with open("static/style.css") as f:
            self.css = f.read()

    def test_has_active_board_rule(self):
        self.assertIn("active", self.css)

    def test_has_ai_flash_rule(self):
        self.assertIn("ai-flash", self.css)

    def test_has_min_cell_size(self):
        self.assertIn("48", self.css)

    def test_has_inner_border(self):
        self.assertIn("#aaa", self.css)

    def test_has_subboard_border(self):
        self.assertIn("#333", self.css)

    def test_has_vmin_or_responsive(self):
        self.assertTrue("vmin" in self.css or "max-width" in self.css or
                        "responsive" in self.css.lower())

if __name__ == "__main__":
    unittest.main()
