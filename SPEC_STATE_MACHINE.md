# SPEC_STATE_MACHINE.md — State Machine

---

## Overview

The state machine tracks the full conversational context at every turn. It lives in `backend/state_machine.py` and is the central coordinator between the classifier output, the RAG query, and the generator call.

---

## State Structure

The full state at any moment is the combination of **topic × stage × tone**.

```python
state = {
    "topic": str,               # current topic key
    "stage": str,               # current stage key
    "tone": str,                # current tone key
    "score": int,               # 0-100, evaluation score
    "stage_turn_count": int,    # turns elapsed in current stage
    "tone_signal_count": int,   # consecutive signals toward pending tone transition
    "topic_index": int,         # 0-3, position in linear topic graph
    "conversation_complete": bool
}
```

---

## Topics

Linear graph — traversal is strictly sequential, no branching.

```
deception → self_knowledge → adaptability → victory
```

| Key | Display Name | Description |
|---|---|---|
| `deception` | Deception & Appearance | All warfare is based on deception. The gap between what is real and what is shown. |
| `self_knowledge` | Self-Knowledge & Knowing the Enemy | Know yourself, know your enemy. Intelligence, observation, understanding. |
| `adaptability` | Adaptability & Wu Wei | Responding to circumstances rather than forcing them. Water as metaphor. |
| `victory` | Victory Without Fighting | The supreme art is subduing the enemy without battle. Strategic patience. |

---

## Stages

Stages progress sequentially within each topic. Stage advancement requires **both**:
- Minimum 2 turns elapsed in the current stage (`stage_turn_count >= 2`)
- A positive classifier signal in the current turn (`understanding` or `insight`)

| Key | Description | SUNZI Behavior |
|---|---|---|
| `introduction` | SUNZI presents the topic and orients the student | Delivers opening passage, asks first question. Tone defaults to Neutral. |
| `examination` | SUNZI probes the student's understanding | Active back-and-forth. All tone transitions fully active. |
| `challenge` | SUNZI introduces a paradox or harder problem | More pointed questioning. Draws on contradiction within the text. |
| `resolution` | Conversation reaches conclusion or productive uncertainty | SUNZI delivers verdict on this topic before advancing. |

After `resolution` completes, advance `topic_index` by 1. If `topic_index` reaches 4, set `conversation_complete: true`.

---

## Tone States

### Definitions

| Key | Display Name | Description |
|---|---|---|
| `neutral` | Neutral / Evaluating | Default state. Cold, precise, observational. No affect. |
| `probing` | Probing | Narrowed questions, increased pressure. Student has given weak responses. |
| `contemptuous` | Contemptuous | Surgical. Uses student's own words against them. Slow to trigger, slow to leave. |
| `illuminated` | Illuminated | Brief flash of genuine engagement. Rare. Decays immediately after one exchange. |
| `recalibrating` | Recalibrating | Off-topic input detected. Cold, mechanical. Flags and redirects. |

---

### Transition Rules

#### Immediate Transitions (take effect on the triggering turn)

| Trigger | From | To |
|---|---|---|
| Classification: `insight` | Any | `illuminated` |
| Classification: `off_topic` | Any | `recalibrating` |
| Tone: `illuminated` (decay) | `illuminated` | `neutral` (after 1 exchange) |
| Tone: `recalibrating` (return) | `recalibrating` | previous tone (once student re-engages) |

#### Weighted Transitions (require 2 consecutive matching signals)

Track consecutive signal count in `tone_signal_count`. Reset to 0 when a non-matching signal is received.

| Signal streak | From | To |
|---|---|---|
| 2x `confusion` or `evasion` | `neutral` | `probing` |
| 2x `confusion` or `evasion` | `probing` | `contemptuous` |
| 2x `understanding` | `contemptuous` | `neutral` |
| 2x `understanding` | `probing` | `neutral` |

#### Special Case: Contemptuous → Illuminated

If classification is `insight` while tone is `contemptuous`, transition directly to `illuminated` (immediate). This is the highest-value dramatic moment in the system. Do not require weighting.

---

## Classification Categories

The classifier returns one of these six string values:

| Value | Meaning |
|---|---|
| `understanding` | Student demonstrates grasp of the concept |
| `confusion` | Student expresses or displays confusion |
| `insight` | Student offers a surprising or genuinely insightful response |
| `clarification` | Student asks a clarifying question |
| `evasion` | Student gives a minimal, deflective, or non-answer |
| `off_topic` | Input is off-topic, anachronistic, or nonsensical |

---

## Scoring

Score starts at 50 (neutral baseline). Adjust on each turn based on classification:

| Classification | Score Delta |
|---|---|
| `insight` | +10 |
| `understanding` | +5 |
| `clarification` | +0 |
| `confusion` | -3 |
| `evasion` | -5 |
| `off_topic` | -7 |

Clamp score to range [0, 100] at all times.

---

## State Machine Implementation

```python
class StateMachine:
    def __init__(self):
        self.sessions = {}  # session_id -> state dict

    def get_state(self, session_id: str) -> dict:
        # Return state for session, initialize if new

    def process_turn(self, session_id: str, classification: str) -> dict:
        # Apply classification to current state
        # Update tone (immediate or weighted)
        # Update score
        # Check stage advancement conditions
        # Check topic advancement conditions
        # Return updated state

    def reset(self, session_id: str) -> dict:
        # Reset session to initial state
```

**Initial state for new sessions:**
```python
{
    "topic": "deception",
    "stage": "introduction",
    "tone": "neutral",
    "score": 50,
    "stage_turn_count": 0,
    "tone_signal_count": 0,
    "topic_index": 0,
    "conversation_complete": False
}
```

---

## State Transition Summary Diagram

```
Classifications → Tone Transitions:

insight ──────────────────────────────→ illuminated (immediate, from any state)
off_topic ────────────────────────────→ recalibrating (immediate, from any state)

neutral ──[2x confusion/evasion]──────→ probing
probing ──[2x confusion/evasion]──────→ contemptuous
probing ──[2x understanding]──────────→ neutral
contemptuous ──[2x understanding]─────→ neutral
contemptuous ──[insight]──────────────→ illuminated (immediate)

illuminated ──[next turn]─────────────→ neutral (automatic decay)
recalibrating ──[re-engagement]───────→ previous tone (automatic return)
```