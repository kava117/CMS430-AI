TOPICS = ["deception", "self_knowledge", "adaptability", "victory"]
STAGES = ["introduction", "examination", "challenge", "resolution"]

# Classifications that count as positive signals for stage advancement
ADVANCE_SIGNALS = {"insight", "understanding"}

# Classifications that push toward probing/contemptuous
NEGATIVE_SIGNALS = {"confusion", "evasion"}

DIFFICULTY_SETTINGS = {
    "easy": {
        "score_deltas": {
            "insight": 12,
            "understanding": 5,
            "clarification": 0,
            "confusion": -3,
            "evasion": -4,
            "off_topic": -5,
        },
        "tone_threshold": 3,
        "stage_advance_min_turns": 1,
        "initial_score": 50,
    },
    "normal": {
        "score_deltas": {
            "insight": 10,
            "understanding": 4,
            "clarification": -2,
            "confusion": -6,
            "evasion": -8,
            "off_topic": -10,
        },
        "tone_threshold": 2,
        "stage_advance_min_turns": 2,
        "initial_score": 25,
    },
    "hard": {
        "score_deltas": {
            "insight": 8,
            "understanding": 3,
            "clarification": -3,
            "confusion": -8,
            "evasion": -10,
            "off_topic": -12,
        },
        "tone_threshold": 2,
        "stage_advance_min_turns": 2,
        "initial_score": 0,
    },
}


def _initial_state(difficulty: str = "normal") -> dict:
    settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["normal"])
    return {
        "topic": "deception",
        "stage": "introduction",
        "tone": "neutral",
        "score": settings["initial_score"],
        "stage_turn_count": 0,
        "tone_signal_count": 0,
        "topic_index": 0,
        "conversation_complete": False,
        "difficulty": difficulty,
        "_prev_tone": "neutral",  # internal: tracks tone before recalibrating
        "_tone_signal_dir": None,  # internal: "up" (toward neutral) or "down" (toward contemptuous)
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

        settings = DIFFICULTY_SETTINGS.get(state.get("difficulty", "normal"), DIFFICULTY_SETTINGS["normal"])

        # 1. Update score
        delta = settings["score_deltas"].get(classification, 0)
        state["score"] = max(0, min(100, state["score"] + delta))

        # 2. Update tone
        _update_tone(state, classification, settings["tone_threshold"])

        # 3. Update stage turn count and check advancement
        state["stage_turn_count"] += 1
        _check_stage_advance(state, classification, settings["stage_advance_min_turns"])

        return _public_state(state)

    def set_difficulty(self, session_id: str, difficulty: str, update_score: bool = False) -> dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = _initial_state(difficulty)
        else:
            self.sessions[session_id]["difficulty"] = difficulty
            if update_score:
                settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["normal"])
                self.sessions[session_id]["score"] = settings["initial_score"]
        return _public_state(self.sessions[session_id])

    def reset(self, session_id: str, difficulty: str = "normal") -> dict:
        self.sessions[session_id] = _initial_state(difficulty)
        return _public_state(self.sessions[session_id])

    def debug_advance(self, session_id: str) -> dict:
        """Force-advance to the next stage, bypassing turn count and classification requirements."""
        if session_id not in self.sessions:
            self.sessions[session_id] = _initial_state()
        state = self.sessions[session_id]
        if state["conversation_complete"]:
            return _public_state(state)

        current_stage_idx = STAGES.index(state["stage"])
        if current_stage_idx < len(STAGES) - 1:
            state["stage"] = STAGES[current_stage_idx + 1]
            state["stage_turn_count"] = 0
        else:
            state["topic_index"] += 1
            if state["topic_index"] >= len(TOPICS):
                state["conversation_complete"] = True
            else:
                state["topic"] = TOPICS[state["topic_index"]]
                state["stage"] = STAGES[0]
                state["stage_turn_count"] = 0

        return _public_state(state)


def _reset_signal_count(state: dict):
    state["tone_signal_count"] = 0
    state["_tone_signal_dir"] = None


def _update_tone(state: dict, classification: str, tone_threshold: int = 2):
    current_tone = state["tone"]

    # Illuminated decays to neutral automatically on the next turn
    if current_tone == "illuminated":
        state["tone"] = "neutral"
        state["_prev_tone"] = "neutral"
        current_tone = "neutral"
        _reset_signal_count(state)

    # Immediate transitions
    if classification == "insight":
        state["_prev_tone"] = current_tone if current_tone != "recalibrating" else state["_prev_tone"]
        state["tone"] = "illuminated"
        _reset_signal_count(state)
        return

    if classification == "off_topic":
        if current_tone != "recalibrating":
            state["_prev_tone"] = current_tone
        state["tone"] = "recalibrating"
        _reset_signal_count(state)
        return

    # Return from recalibrating on any non-off_topic signal
    if current_tone == "recalibrating":
        state["tone"] = state["_prev_tone"]
        current_tone = state["tone"]
        _reset_signal_count(state)

    # Weighted transitions
    if classification in NEGATIVE_SIGNALS:
        if current_tone in ("neutral", "probing"):
            if state["_tone_signal_dir"] != "down":
                # Direction switched — reset before accumulating
                _reset_signal_count(state)
                state["_tone_signal_dir"] = "down"
            state["tone_signal_count"] += 1
            if state["tone_signal_count"] >= tone_threshold:
                if current_tone == "neutral":
                    state["tone"] = "probing"
                elif current_tone == "probing":
                    state["tone"] = "contemptuous"
                _reset_signal_count(state)
        else:
            # In contemptuous, negative signals don't change tone
            _reset_signal_count(state)

    elif classification == "understanding":
        if current_tone in ("probing", "contemptuous"):
            if state["_tone_signal_dir"] != "up":
                # Direction switched — reset before accumulating
                _reset_signal_count(state)
                state["_tone_signal_dir"] = "up"
            state["tone_signal_count"] += 1
            if state["tone_signal_count"] >= tone_threshold:
                state["tone"] = "neutral"
                _reset_signal_count(state)
        else:
            _reset_signal_count(state)

    else:
        # clarification or other: reset signal count, no tone change
        _reset_signal_count(state)


def _check_stage_advance(state: dict, classification: str, min_turns: int = 2):
    if classification not in ADVANCE_SIGNALS:
        return
    if state["stage_turn_count"] < min_turns:
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
