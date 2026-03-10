"""
Integration tests — full pipeline through Flask test client.
All LLM calls are mocked. No real API calls.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client(mocker):
    mocker.patch("app.classify_input", return_value="understanding")
    mocker.patch("app.generate_response", return_value="SUNZI speaks.")
    mocker.patch("app._get_rag_results", return_value=[])

    import app as flask_app
    flask_app.state_machine.sessions.clear()
    flask_app.session_histories.clear()
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c


def _turn(client, session_id="s1", user_input="my answer", classification=None, mocker=None):
    if classification and mocker:
        mocker.patch("app.classify_input", return_value=classification)
    return client.post("/api/turn", json={"user_input": user_input, "session_id": session_id})


# --- Full pipeline flow ---

def test_full_turn_returns_valid_json(client):
    r = _turn(client)
    data = r.get_json()
    assert "response_text" in data
    assert "state" in data
    assert "classification" in data
    assert data["response_text"] == "SUNZI speaks."


def test_state_has_all_required_keys(client):
    r = _turn(client)
    state = r.get_json()["state"]
    for key in ["topic", "stage", "tone", "score", "stage_turn_count",
                "tone_signal_count", "topic_index", "conversation_complete"]:
        assert key in state


def test_score_accumulates_over_turns(mocker, client):
    mocker.patch("app.classify_input", return_value="understanding")
    _turn(client)  # +5 → 55
    _turn(client)  # +5 → 60... but turn 2 advances stage, keeping count 0
    # At least score changed
    r = _turn(client)
    assert r.get_json()["state"]["score"] > 50


def test_two_confusion_turns_produce_probing(mocker, client):
    mocker.patch("app.classify_input", return_value="confusion")
    _turn(client)
    r = _turn(client)
    assert r.get_json()["state"]["tone"] == "probing"


def test_insight_produces_illuminated(mocker, client):
    mocker.patch("app.classify_input", return_value="insight")
    r = _turn(client)
    assert r.get_json()["state"]["tone"] == "illuminated"


def test_stage_advances_with_understanding_after_two_turns(mocker, client):
    mocker.patch("app.classify_input", return_value="clarification")
    _turn(client)  # count = 1
    _turn(client)  # count = 2
    mocker.patch("app.classify_input", return_value="understanding")
    r = _turn(client)  # advance
    assert r.get_json()["state"]["stage"] == "examination"


def test_reset_then_get_returns_initial(client):
    _turn(client)
    client.post("/api/reset", json={"session_id": "s1"})
    r = client.get("/api/state/s1")
    state = r.get_json()
    assert state["score"] == 50
    assert state["stage_turn_count"] == 0
    assert state["topic"] == "deception"


def test_history_grows_over_multiple_turns(mocker, client):
    received_histories = []

    def capture_generate(user_input, state, classification, rag_context, history):
        received_histories.append(list(history))
        return "SUNZI speaks."

    mocker.patch("app.generate_response", side_effect=capture_generate)
    _turn(client)
    _turn(client)
    _turn(client)
    # Each turn appends 2 entries; by turn 3 generator receives 4 entries
    assert len(received_histories[-1]) == 4
