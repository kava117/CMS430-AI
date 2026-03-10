TOPICS = ["deception", "self_knowledge", "adaptability", "victory"]
STAGES = ["introduction", "examination", "challenge", "resolution"]

SCORE_DELTAS = {
    "insight": 10,
    "understanding": 5,
    "clarification": 0,
    "confusion": -3,
    "evasion": -5,
    "off_topic": -7,
}

# Classifications that count as positive signals for stage advancement
ADVANCE_SIGNALS = {"insight", "understanding"}

# Classifications that push toward probing/contemptuous
NEGATIVE_SIGNALS = {"confusion", "evasion"}


def _initial_state() -> dict:
    return {
        "topic": "deception",
        "stage": "introduction",
        "tone": "neutral",
        "score": 50,
        "stage_turn_count": 0,
        "tone_signal_count": 0,
        "topic_index": 0,
        "conversation_complete": False,
        "_prev_tone": "neutral",  # internal: tracks tone before recalibrating
    }


class StateMachine:
    def __init__(self):
        self.sessions: dict[str, dict] = {}

    def get_state(self, session_id: str) -> dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = _initial_state()
        return _public_state(self.sessions[session_id])

    def process_turn(self, session_id: str, classification: str) -> dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = _initial_state()
        state = self.sessions[session_id]

        if state["conversation_complete"]:
            return _public_state(state)

        # 1. Update score
        delta = SCORE_DELTAS.get(classification, 0)
        state["score"] = max(0, min(100, state["score"] + delta))

        # 2. Update tone
        _update_tone(state, classification)

        # 3. Update stage turn count and check advancement
        state["stage_turn_count"] += 1
        _check_stage_advance(state, classification)

        return _public_state(state)

    def reset(self, session_id: str) -> dict:
        self.sessions[session_id] = _initial_state()
        return _public_state(self.sessions[session_id])


def _update_tone(state: dict, classification: str):
    current_tone = state["tone"]

    # Illuminated decays to neutral automatically on the next turn
    if current_tone == "illuminated":
        state["tone"] = "neutral"
        state["_prev_tone"] = "neutral"
        current_tone = "neutral"

    # Immediate transitions
    if classification == "insight":
        state["_prev_tone"] = current_tone if current_tone != "recalibrating" else state["_prev_tone"]
        state["tone"] = "illuminated"
        state["tone_signal_count"] = 0
        return

    if classification == "off_topic":
        if current_tone != "recalibrating":
            state["_prev_tone"] = current_tone
        state["tone"] = "recalibrating"
        state["tone_signal_count"] = 0
        return

    # Return from recalibrating on any non-off_topic signal
    if current_tone == "recalibrating":
        state["tone"] = state["_prev_tone"]
        current_tone = state["tone"]
        state["tone_signal_count"] = 0

    # Weighted transitions
    if classification in NEGATIVE_SIGNALS:
        if current_tone in ("neutral", "probing"):
            state["tone_signal_count"] += 1
            if state["tone_signal_count"] >= 2:
                if current_tone == "neutral":
                    state["tone"] = "probing"
                elif current_tone == "probing":
                    state["tone"] = "contemptuous"
                state["tone_signal_count"] = 0
        else:
            # In contemptuous, negative signals don't change tone
            state["tone_signal_count"] = 0

    elif classification == "understanding":
        if current_tone in ("probing", "contemptuous"):
            state["tone_signal_count"] += 1
            if state["tone_signal_count"] >= 2:
                state["tone"] = "neutral"
                state["tone_signal_count"] = 0
        else:
            state["tone_signal_count"] = 0

    else:
        # clarification or other: reset signal count, no tone change
        state["tone_signal_count"] = 0


def _check_stage_advance(state: dict, classification: str):
    if classification not in ADVANCE_SIGNALS:
        return
    if state["stage_turn_count"] < 2:
        return

    current_stage_idx = STAGES.index(state["stage"])

    if current_stage_idx < len(STAGES) - 1:
        # Advance to next stage within topic
        state["stage"] = STAGES[current_stage_idx + 1]
        state["stage_turn_count"] = 0
    else:
        # Resolution complete — advance topic
        state["topic_index"] += 1
        if state["topic_index"] >= len(TOPICS):
            state["conversation_complete"] = True
        else:
            state["topic"] = TOPICS[state["topic_index"]]
            state["stage"] = STAGES[0]
            state["stage_turn_count"] = 0


def _public_state(state: dict) -> dict:
    """Return state dict without internal keys."""
    return {k: v for k, v in state.items() if not k.startswith("_")}
