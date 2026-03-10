import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_machine import StateMachine, TOPICS, STAGES


@pytest.fixture
def sm():
    return StateMachine()


# --- Initialization ---

def test_new_session_initial_state(sm):
    state = sm.get_state("s1")
    assert state["topic"] == "deception"
    assert state["stage"] == "introduction"
    assert state["tone"] == "neutral"
    assert state["score"] == 50
    assert state["stage_turn_count"] == 0
    assert state["tone_signal_count"] == 0
    assert state["topic_index"] == 0
    assert state["conversation_complete"] == False


def test_same_session_returns_same_state(sm):
    sm.get_state("s1")
    sm.process_turn("s1", "understanding")
    state = sm.get_state("s1")
    assert state["stage_turn_count"] == 1


def test_different_sessions_are_independent(sm):
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")
    state_a = sm.get_state("s1")
    state_b = sm.get_state("s2")
    assert state_a["tone"] == "probing"
    assert state_b["tone"] == "neutral"


def test_reset_returns_to_initial(sm):
    sm.process_turn("s1", "insight")
    sm.process_turn("s1", "confusion")
    state = sm.reset("s1")
    assert state["tone"] == "neutral"
    assert state["score"] == 50
    assert state["stage_turn_count"] == 0
    assert state["topic"] == "deception"


def test_public_state_has_no_private_keys(sm):
    state = sm.get_state("s1")
    for key in state:
        assert not key.startswith("_"), f"Private key exposed: {key}"


# --- Scoring ---

def test_score_insight(sm):
    state = sm.process_turn("s1", "insight")
    assert state["score"] == 60


def test_score_understanding(sm):
    state = sm.process_turn("s1", "understanding")
    assert state["score"] == 55


def test_score_clarification(sm):
    state = sm.process_turn("s1", "clarification")
    assert state["score"] == 50


def test_score_confusion(sm):
    state = sm.process_turn("s1", "confusion")
    assert state["score"] == 47


def test_score_evasion(sm):
    state = sm.process_turn("s1", "evasion")
    assert state["score"] == 45


def test_score_off_topic(sm):
    state = sm.process_turn("s1", "off_topic")
    assert state["score"] == 43


def test_score_clamps_at_100(sm):
    for _ in range(10):
        sm.process_turn("s1", "insight")
    state = sm.get_state("s1")
    assert state["score"] == 100


def test_score_clamps_at_0(sm):
    sm.sessions["s1"] = {"topic": "deception", "stage": "introduction", "tone": "neutral",
                          "score": 5, "stage_turn_count": 0, "tone_signal_count": 0,
                          "topic_index": 0, "conversation_complete": False, "_prev_tone": "neutral"}
    sm.process_turn("s1", "off_topic")
    state = sm.get_state("s1")
    assert state["score"] == 0


# --- Tone: Immediate transitions ---

def test_insight_from_neutral_goes_to_illuminated(sm):
    state = sm.process_turn("s1", "insight")
    assert state["tone"] == "illuminated"


def test_insight_from_probing_goes_to_illuminated(sm):
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")
    assert sm.get_state("s1")["tone"] == "probing"
    state = sm.process_turn("s1", "insight")
    assert state["tone"] == "illuminated"


def test_insight_from_contemptuous_goes_to_illuminated(sm):
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")
    assert sm.get_state("s1")["tone"] == "contemptuous"
    state = sm.process_turn("s1", "insight")
    assert state["tone"] == "illuminated"


def test_off_topic_goes_to_recalibrating(sm):
    state = sm.process_turn("s1", "off_topic")
    assert state["tone"] == "recalibrating"


def test_off_topic_from_probing_goes_to_recalibrating(sm):
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")
    state = sm.process_turn("s1", "off_topic")
    assert state["tone"] == "recalibrating"


def test_illuminated_decays_to_neutral_next_turn(sm):
    sm.process_turn("s1", "insight")
    assert sm.get_state("s1")["tone"] == "illuminated"
    state = sm.process_turn("s1", "clarification")
    assert state["tone"] == "neutral"


def test_recalibrating_returns_to_previous_tone(sm):
    # Go to probing, then recalibrate, then re-engage
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")
    assert sm.get_state("s1")["tone"] == "probing"
    sm.process_turn("s1", "off_topic")
    assert sm.get_state("s1")["tone"] == "recalibrating"
    state = sm.process_turn("s1", "understanding")
    assert state["tone"] == "probing"


def test_recalibrating_from_neutral_returns_to_neutral(sm):
    sm.process_turn("s1", "off_topic")
    state = sm.process_turn("s1", "clarification")
    assert state["tone"] == "neutral"


# --- Tone: Weighted transitions ---

def test_one_confusion_does_not_trigger_probing(sm):
    state = sm.process_turn("s1", "confusion")
    assert state["tone"] == "neutral"


def test_two_confusion_triggers_probing(sm):
    sm.process_turn("s1", "confusion")
    state = sm.process_turn("s1", "confusion")
    assert state["tone"] == "probing"


def test_evasion_plus_confusion_triggers_probing(sm):
    sm.process_turn("s1", "evasion")
    state = sm.process_turn("s1", "confusion")
    assert state["tone"] == "probing"


def test_two_confusion_from_probing_triggers_contemptuous(sm):
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")  # -> probing
    sm.process_turn("s1", "confusion")
    state = sm.process_turn("s1", "confusion")  # -> contemptuous
    assert state["tone"] == "contemptuous"


def test_one_understanding_from_probing_does_not_trigger_neutral(sm):
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")  # -> probing
    state = sm.process_turn("s1", "understanding")
    assert state["tone"] == "probing"


def test_two_understanding_from_probing_triggers_neutral(sm):
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")  # -> probing
    sm.process_turn("s1", "understanding")
    state = sm.process_turn("s1", "understanding")
    assert state["tone"] == "neutral"


def test_two_understanding_from_contemptuous_triggers_neutral(sm):
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")  # -> probing
    sm.process_turn("s1", "confusion")
    sm.process_turn("s1", "confusion")  # -> contemptuous
    sm.process_turn("s1", "understanding")
    state = sm.process_turn("s1", "understanding")
    assert state["tone"] == "neutral"


def test_non_matching_signal_resets_count(sm):
    sm.process_turn("s1", "confusion")  # count = 1
    sm.process_turn("s1", "clarification")  # reset
    state = sm.process_turn("s1", "confusion")  # count = 1 again
    assert state["tone"] == "neutral"
    assert state["tone_signal_count"] == 1


# --- Stage advancement ---

def test_stage_turn_count_increments(sm):
    sm.process_turn("s1", "clarification")
    state = sm.process_turn("s1", "clarification")
    assert state["stage_turn_count"] == 2


def test_no_advance_on_turn_1_with_understanding(sm):
    state = sm.process_turn("s1", "understanding")
    assert state["stage"] == "introduction"


def test_advance_on_understanding_with_enough_turns(sm):
    sm.process_turn("s1", "clarification")
    sm.process_turn("s1", "clarification")  # stage_turn_count = 2
    state = sm.process_turn("s1", "understanding")
    assert state["stage"] == "examination"


def test_advance_on_insight_with_enough_turns(sm):
    sm.process_turn("s1", "clarification")
    sm.process_turn("s1", "clarification")
    state = sm.process_turn("s1", "insight")
    assert state["stage"] == "examination"


def test_no_advance_on_confusion_with_enough_turns(sm):
    sm.process_turn("s1", "clarification")
    sm.process_turn("s1", "clarification")
    state = sm.process_turn("s1", "confusion")
    assert state["stage"] == "introduction"


def test_no_advance_on_evasion_with_enough_turns(sm):
    sm.process_turn("s1", "clarification")
    sm.process_turn("s1", "clarification")
    state = sm.process_turn("s1", "evasion")
    assert state["stage"] == "introduction"


def test_stage_turn_count_resets_on_advance(sm):
    sm.process_turn("s1", "clarification")
    sm.process_turn("s1", "clarification")
    state = sm.process_turn("s1", "understanding")
    assert state["stage_turn_count"] == 0


def _advance_through_stage(sm, session_id):
    """Helper: advance one stage by doing 2 turns + understanding."""
    sm.process_turn(session_id, "clarification")
    sm.process_turn(session_id, "clarification")
    sm.process_turn(session_id, "understanding")


def test_full_stage_traversal_within_topic(sm):
    for expected_stage in ["examination", "challenge", "resolution"]:
        _advance_through_stage(sm, "s1")
        assert sm.get_state("s1")["stage"] == expected_stage


# --- Topic advancement ---

def _advance_through_topic(sm, session_id):
    """Helper: advance through all 4 stages of a topic."""
    for _ in range(4):
        _advance_through_stage(sm, session_id)


def test_topic_advances_after_resolution(sm):
    _advance_through_topic(sm, "s1")
    state = sm.get_state("s1")
    assert state["topic"] == "self_knowledge"
    assert state["topic_index"] == 1
    assert state["stage"] == "introduction"


def test_full_topic_sequence(sm):
    for expected_topic in ["self_knowledge", "adaptability", "victory"]:
        _advance_through_topic(sm, "s1")
        assert sm.get_state("s1")["topic"] == expected_topic


def test_conversation_complete_after_all_topics(sm):
    for _ in range(4):
        _advance_through_topic(sm, "s1")
    state = sm.get_state("s1")
    assert state["conversation_complete"] == True


def test_no_further_changes_after_complete(sm):
    for _ in range(4):
        _advance_through_topic(sm, "s1")
    score_before = sm.get_state("s1")["score"]
    sm.process_turn("s1", "insight")
    assert sm.get_state("s1")["score"] == score_before
