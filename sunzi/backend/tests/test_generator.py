import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator import format_rag_context, format_history, FALLBACK_RESPONSE


# --- format_rag_context ---

def test_format_rag_empty_returns_empty():
    assert format_rag_context([]) == ""


def test_format_rag_sun_tzu_only_has_header():
    results = [{"source": "sun_tzu", "chapter": 1, "chapter_title": "Laying Plans", "text": "All warfare is based on deception."}]
    out = format_rag_context(results)
    assert "SUN TZU'S WORDS" in out
    assert "SCHOLARLY CONTEXT" not in out


def test_format_rag_commentary_only_has_header():
    results = [{"source": "commentary", "chapter": 1, "chapter_title": "Laying Plans", "text": "Giles notes that..."}]
    out = format_rag_context(results)
    assert "SCHOLARLY CONTEXT" in out
    assert "SUN TZU'S WORDS" not in out


def test_format_rag_mixed_has_both_headers():
    results = [
        {"source": "sun_tzu", "chapter": 1, "chapter_title": "Laying Plans", "text": "Sun Tzu said."},
        {"source": "commentary", "chapter": 1, "chapter_title": "Laying Plans", "text": "Giles notes."},
    ]
    out = format_rag_context(results)
    assert "SUN TZU'S WORDS" in out
    assert "SCHOLARLY CONTEXT" in out


def test_format_rag_sun_tzu_first_in_output():
    results = [
        {"source": "commentary", "chapter": 1, "chapter_title": "Laying Plans", "text": "Giles notes."},
        {"source": "sun_tzu", "chapter": 1, "chapter_title": "Laying Plans", "text": "Sun Tzu said."},
    ]
    out = format_rag_context(results)
    assert out.index("SUN TZU'S WORDS") < out.index("SCHOLARLY CONTEXT")


def test_format_rag_sun_tzu_includes_chapter_attribution():
    results = [{"source": "sun_tzu", "chapter": 3, "chapter_title": "Attack by Stratagem", "text": "Text here."}]
    out = format_rag_context(results)
    assert "[Chapter 3: Attack by Stratagem]" in out


def test_format_rag_commentary_has_no_chapter_attribution():
    results = [{"source": "commentary", "chapter": 1, "chapter_title": "Laying Plans", "text": "Commentary text."}]
    out = format_rag_context(results)
    assert "[Chapter" not in out


# --- format_history ---

def test_format_history_empty_returns_empty():
    assert format_history([]) == ""


def test_format_history_user_turn_label():
    history = [{"role": "user", "content": "Hello"}]
    out = format_history(history)
    assert out == "STUDENT: Hello"


def test_format_history_sunzi_turn_label():
    history = [{"role": "sunzi", "content": "Assessment begins."}]
    out = format_history(history)
    assert out == "SUNZI: Assessment begins."


def test_format_history_truncates_to_12():
    history = [{"role": "user", "content": f"msg{i}"} for i in range(20)]
    out = format_history(history)
    lines = out.strip().split("\n")
    assert len(lines) == 12


def test_format_history_exactly_12_returns_all():
    history = [{"role": "user", "content": f"msg{i}"} for i in range(12)]
    out = format_history(history)
    lines = out.strip().split("\n")
    assert len(lines) == 12


def test_format_history_labels_are_correct():
    history = [
        {"role": "user", "content": "My answer"},
        {"role": "sunzi", "content": "SUNZI response"},
    ]
    out = format_history(history)
    assert "STUDENT: My answer" in out
    assert "SUNZI: SUNZI response" in out
    assert "user:" not in out
    assert "assistant:" not in out


# --- generate_response (mocked API) ---

@pytest.fixture
def mock_openai(mocker):
    mock_client = MagicMock()
    mocker.patch("generator.client", mock_client)
    return mock_client


def _make_mock_response(text: str):
    mock = MagicMock()
    mock.choices[0].message.content = text
    return mock


def test_generate_response_returns_string(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("The general who wins.")
    from generator import generate_response
    result = generate_response("my input", {"topic": "deception", "stage": "introduction", "tone": "neutral", "score": 50},
                               "understanding", "some context", [])
    assert result == "The general who wins."


def test_generate_response_model_is_gpt4o(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("response")
    from generator import generate_response
    generate_response("input", {"topic": "deception", "stage": "introduction", "tone": "neutral", "score": 50},
                      "understanding", "", [])
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4o"


def test_generate_response_temperature_is_07(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("response")
    from generator import generate_response
    generate_response("input", {"topic": "deception", "stage": "introduction", "tone": "neutral", "score": 50},
                      "understanding", "", [])
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["temperature"] == 0.7


def test_generate_response_max_tokens_300(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("response")
    from generator import generate_response
    generate_response("input", {"topic": "deception", "stage": "introduction", "tone": "neutral", "score": 50},
                      "understanding", "", [])
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["max_tokens"] == 300


def test_generate_response_turn_prompt_includes_state(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("response")
    from generator import generate_response
    generate_response("my input", {"topic": "adaptability", "stage": "challenge", "tone": "probing", "score": 65},
                      "confusion", "context", [])
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    user_content = call_kwargs["messages"][1]["content"]
    assert "adaptability" in user_content
    assert "challenge" in user_content
    assert "probing" in user_content
    assert "65" in user_content
    assert "confusion" in user_content


def test_generate_response_turn_prompt_includes_rag(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("response")
    from generator import generate_response
    generate_response("input", {"topic": "deception", "stage": "introduction", "tone": "neutral", "score": 50},
                      "understanding", "SUN TZU'S WORDS: Chapter 1...", [])
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    user_content = call_kwargs["messages"][1]["content"]
    assert "SUN TZU'S WORDS" in user_content


def test_generate_response_system_prompt_is_generator_prompt(mock_openai):
    mock_openai.chat.completions.create.return_value = _make_mock_response("response")
    from generator import generate_response
    from character import GENERATOR_SYSTEM_PROMPT
    generate_response("input", {"topic": "deception", "stage": "introduction", "tone": "neutral", "score": 50},
                      "understanding", "", [])
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["messages"][0]["content"] == GENERATOR_SYSTEM_PROMPT


def test_generate_response_api_error_returns_fallback(mock_openai):
    mock_openai.chat.completions.create.side_effect = Exception("API down")
    from generator import generate_response
    result = generate_response("input", {"topic": "deception", "stage": "introduction", "tone": "neutral", "score": 50},
                               "understanding", "", [])
    assert result == FALLBACK_RESPONSE
