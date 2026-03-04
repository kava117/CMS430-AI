import unittest, json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import app as flask_app

class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        flask_app.app.config["TESTING"] = True
        flask_app.app.config["SECRET_KEY"] = "test-secret"
        self.client = flask_app.app.test_client()

    def _new_game(self, difficulty="easy", human_plays="X"):
        return self.client.post("/api/new_game",
            data=json.dumps({"difficulty": difficulty, "human_plays": human_plays}),
            content_type="application/json")

    def test_index_returns_200(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)

    def test_new_game_returns_state(self):
        r = self._new_game()
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("state", data)

    def test_new_game_human_x_no_ai_move(self):
        r = self._new_game(human_plays="X")
        data = json.loads(r.data)
        self.assertIsNone(data["ai_move"])

    def test_new_game_human_o_has_ai_move(self):
        r = self._new_game(difficulty="easy", human_plays="O")
        data = json.loads(r.data)
        self.assertIsNotNone(data["ai_move"])
        self.assertIsInstance(data["ai_move"], list)
        self.assertEqual(len(data["ai_move"]), 2)

    def test_move_accepted(self):
        self._new_game(human_plays="X")
        r = self.client.post("/api/move",
            data=json.dumps({"board_index": 4, "cell_index": 4}),
            content_type="application/json")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsNone(data.get("error"))

    def test_invalid_move_returns_error(self):
        self._new_game(human_plays="X")
        # Make a valid first move
        self.client.post("/api/move",
            data=json.dumps({"board_index": 0, "cell_index": 0}),
            content_type="application/json")
        # Attempt to play in the same cell
        r = self.client.post("/api/move",
            data=json.dumps({"board_index": 0, "cell_index": 0}),
            content_type="application/json")
        data = json.loads(r.data)
        self.assertIsNotNone(data.get("error"))

    def test_get_state_returns_dict(self):
        self._new_game(human_plays="X")
        r = self.client.get("/api/state")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("board", data)
        self.assertIn("meta_board", data)

    def test_move_returns_ai_move(self):
        self._new_game(difficulty="easy", human_plays="X")
        r = self.client.post("/api/move",
            data=json.dumps({"board_index": 4, "cell_index": 4}),
            content_type="application/json")
        data = json.loads(r.data)
        self.assertIsNotNone(data.get("ai_move"))

if __name__ == "__main__":
    unittest.main()
