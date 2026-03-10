import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_mock_response(classification: str):
    """Build a mock OpenAI response object."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({"classification": classification})
    return mock_response


@pytest.fixture(autouse=True)
def mock_openai(mocker):
    mock_client = MagicMock()
    mocker.patch("classifier.client", mock_client)
    return mock_client


def test_returns_understanding(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("understanding")
    from classifier import classify_input
    assert classify_input("I understand", "deception", "introduction") == "understanding"


def test_returns_confusion(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("confusion")
    from classifier import classify_input
    assert classify_input("I don't get it", "deception", "introduction") == "confusion"


def test_returns_insight(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("insight")
    from classifier import classify_input
    assert classify_input("Brilliant observation", "deception", "introduction") == "insight"


def test_returns_clarification(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("clarification")
    from classifier import classify_input
    assert classify_input("Can you explain?", "deception", "introduction") == "clarification"


def test_returns_evasion(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("evasion")
    from classifier import classify_input
    assert classify_input("I dunno", "deception", "introduction") == "evasion"


def test_returns_off_topic(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("off_topic")
    from classifier import classify_input
    assert classify_input("What about the internet?", "deception", "introduction") == "off_topic"


def test_invalid_classification_defaults_to_confusion(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("brilliant")
    from classifier import classify_input
    assert classify_input("test", "deception", "introduction") == "confusion"


def test_malformed_json_defaults_to_confusion(mock_openai):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "not json at all"
    mock_openai.chat.completions.create.return_value = mock_response
    from classifier import classify_input
    assert classify_input("test", "deception", "introduction") == "confusion"


def test_api_exception_defaults_to_confusion(mock_openai):
    mock_openai.chat.completions.create.side_effect = Exception("API error")
    from classifier import classify_input
    assert classify_input("test", "deception", "introduction") == "confusion"


def test_api_called_with_correct_model(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("understanding")
    from classifier import classify_input
    classify_input("test", "deception", "introduction")
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4o"


def test_api_called_with_temperature_zero(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("understanding")
    from classifier import classify_input
    classify_input("test", "deception", "introduction")
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["temperature"] == 0


def test_api_called_with_max_tokens_50(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("understanding")
    from classifier import classify_input
    classify_input("test", "deception", "introduction")
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["max_tokens"] == 50


def test_api_called_with_json_object_format(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("understanding")
    from classifier import classify_input
    classify_input("test", "deception", "introduction")
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["response_format"] == {"type": "json_object"}


def test_user_message_contains_topic_and_stage(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("understanding")
    from classifier import classify_input
    classify_input("my answer", "adaptability", "challenge")
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    user_content = call_kwargs["messages"][1]["content"]
    assert "adaptability" in user_content
    assert "challenge" in user_content
