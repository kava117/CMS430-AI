import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VALID_CLASSIFICATIONS = {"understanding", "confusion", "insight", "clarification", "evasion", "off_topic"}
STATE_KEYS = {"topic", "stage", "tone", "score", "stage_turn_count", "tone_signal_count",
              "topic_index", "conversation_complete"}


@pytest.fixture
def client(mocker):
    """Flask test client with mocked LLM calls."""
    mocker.patch("app.classify_input", return_value="understanding")
    mocker.patch("app.generate_response", return_value="SUNZI speaks.")
    mocker.patch("app._get_rag_results", return_value=[])

    import app as flask_app
    # Fresh state for each test
    flask_app.state_machine.sessions.clear()
    flask_app.session_histories.clear()

    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c


def _turn(client, session_id="test-session", user_input="my answer"):
    return client.post("/api/turn", json={"user_input": user_input, "session_id": session_id})


# --- POST /api/turn ---

def test_turn_returns_200(client):
    r = _turn(client)
    assert r.status_code == 200


def test_turn_response_has_required_keys(client):
    r = _turn(client)
    data = r.get_json()
    assert "response_text" in data
    assert "state" in data
    assert "classification" in data


def test_turn_state_has_all_keys(client):
    r = _turn(client)
    state = r.get_json()["state"]
    for key in STATE_KEYS:
        assert key in state, f"Missing state key: {key}"


def test_turn_classification_is_valid(client):
    r = _turn(client)
    assert r.get_json()["classification"] in VALID_CLASSIFICATIONS


def test_turn_missing_user_input_returns_400(client):
    r = client.post("/api/turn", json={"session_id": "s1"})
    assert r.status_code == 400


def test_turn_missing_session_id_returns_400(client):
    r = client.post("/api/turn", json={"user_input": "hello"})
    assert r.status_code == 400


def test_turn_invalid_json_returns_400(client):
    r = client.post("/api/turn", data="not json", content_type="text/plain")
    assert r.status_code == 400


def test_consecutive_turns_increment_stage_turn_count(mocker, client):
    # Use clarification (no stage advance) to keep count climbing
    mocker.patch("app.classify_input", return_value="clarification")
    _turn(client, "s1")
    r = _turn(client, "s1")
    assert r.get_json()["state"]["stage_turn_count"] == 2


def test_different_sessions_are_independent(client):
    _turn(client, "s1")
    _turn(client, "s1")
    r_b = _turn(client, "s2")
    assert r_b.get_json()["state"]["stage_turn_count"] == 1


def test_insight_classification_sets_illuminated_tone(mocker, client):
    mocker.patch("app.classify_input", return_value="insight")
    r = _turn(client)
    assert r.get_json()["state"]["tone"] == "illuminated"


def test_off_topic_classification_sets_recalibrating_tone(mocker, client):
    mocker.patch("app.classify_input", return_value="off_topic")
    r = _turn(client)
    assert r.get_json()["state"]["tone"] == "recalibrating"


def test_llm_exception_returns_fallback(mocker, client):
    mocker.patch("app.generate_response", return_value="INPUT PROCESSING ERROR. RESTATE YOUR RESPONSE.")
    r = _turn(client)
    assert "INPUT PROCESSING ERROR" in r.get_json()["response_text"]


# --- GET /api/state/:session_id ---

def test_get_state_unknown_session_returns_initial(client):
    r = client.get("/api/state/unknown-session")
    assert r.status_code == 200
    state = r.get_json()
    assert state["topic"] == "deception"
    assert state["score"] == 50


def test_get_state_after_turn_returns_updated_state(client):
    _turn(client, "s1")
    r = client.get("/api/state/s1")
    assert r.get_json()["stage_turn_count"] == 1


# --- POST /api/reset ---

def test_reset_returns_initial_state(client):
    _turn(client, "s1")
    _turn(client, "s1")
    r = client.post("/api/reset", json={"session_id": "s1"})
    assert r.status_code == 200
    state = r.get_json()
    assert state["score"] == 50
    assert state["stage_turn_count"] == 0
    assert state["topic"] == "deception"


def test_get_state_after_reset_returns_initial(client):
    _turn(client, "s1")
    client.post("/api/reset", json={"session_id": "s1"})
    r = client.get("/api/state/s1")
    assert r.get_json()["stage_turn_count"] == 0


# --- Conversation history ---

def test_history_grows_with_each_turn(mocker, client):
    captured = {}

    def mock_generate(user_input, state, classification, rag_context, history):
        captured["history"] = list(history)
        return "SUNZI speaks."

    mocker.patch("app.generate_response", side_effect=mock_generate)
    _turn(client, "s1", "first answer")
    _turn(client, "s1", "second answer")
    # On the second turn, history should have 2 entries from turn 1
    assert len(captured["history"]) == 2


def test_history_cleared_on_reset(mocker, client):
    captured = {}

    def mock_generate(user_input, state, classification, rag_context, history):
        captured["history"] = list(history)
        return "SUNZI speaks."

    mocker.patch("app.generate_response", side_effect=mock_generate)
    _turn(client, "s1")
    client.post("/api/reset", json={"session_id": "s1"})
    _turn(client, "s1", "after reset")
    assert captured["history"] == []
