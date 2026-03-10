# SUNZI — Philosophical Assessment System
## Project Overview

---

### Concept

SUNZI is a web application that simulates a conversation with an AI supercomputer set in a cyberpunk future. The AI administers a structured philosophical assessment to the user, drawing from Sun Tzu's *The Art of War* (Giles translation, 1910). The user plays the role of a human subject being evaluated for philosophical and strategic intelligence. The application combines retrieval-augmented generation (RAG), a state machine, a two-step LLM pipeline, and a reactive visual front-end.

The cyberpunk framing is narrative flavor — the core system is a philosophically grounded conversational AI with real state management and RAG-driven responses.

---

### Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | Python + Flask |
| Vector Database | ChromaDB (local) |
| Embeddings | sentence-transformers |
| LLM | OpenAI API (GPT-4o) |
| Source Text | Art of War, Giles translation (Project Gutenberg) |

---

### System Architecture

```
[React Frontend]
      |
      | HTTP (JSON)
      v
[Flask Backend]
      |
      |--- [State Machine] <--- [Classifier LLM Call]
      |         |
      |         v
      |    [ChromaDB RAG Query]
      |         |
      |         v
      +--- [Generator LLM Call]
                |
                v
         [Response JSON]
```

**Data flow per conversational turn:**

1. User submits input via React frontend
2. Flask receives input + current session state
3. **Classifier LLM call** — input is classified into one of six categories
4. State machine processes classification → updates topic, stage, tone
5. **RAG query** — current topic + stage used to retrieve relevant chunks from ChromaDB
6. **Generator LLM call** — takes state, classification, RAG context, conversation history → produces SUNZI's response
7. Flask returns response JSON + updated state to React frontend
8. React updates UI to reflect new tone state, stage progress, topic graph

---

### Conversation Structure

**Topics (linear graph):**
```
Deception & Appearance
        |
        v
Self-Knowledge & Knowing the Enemy
        |
        v
Adaptability & Wu Wei
        |
        v
Victory Without Fighting
```

**Stages (within each topic):**
```
Introduction → Examination → Challenge → Resolution
```

Stage advancement requires: minimum 2 exchanges AND a positive classifier signal.

**Tone States:**
- Neutral / Evaluating (default)
- Probing
- Contemptuous
- Illuminated
- Recalibrating

Tone transitions are driven by classifier output. Most transitions are weighted (require 2 consecutive signals). Illuminated and Recalibrating are immediate.

---

### API Contract

All communication between React and Flask uses JSON over HTTP.

**POST /api/turn**

Request:
```json
{
  "user_input": "string",
  "session_id": "string"
}
```

Response:
```json
{
  "response_text": "string",
  "state": {
    "topic": "deception | self_knowledge | adaptability | victory",
    "stage": "introduction | examination | challenge | resolution",
    "tone": "neutral | probing | contemptuous | illuminated | recalibrating",
    "score": 0-100,
    "stage_turn_count": 0-N,
    "tone_signal_count": 0-N,
    "topic_index": 0-3,
    "conversation_complete": false
  },
  "classification": "understanding | confusion | insight | clarification | evasion | off_topic"
}
```

**GET /api/state/:session_id**

Returns current state object for session restoration.

**POST /api/reset**

Resets session to initial state.

---

### Project File Structure

```
/sunzi
  /backend
    app.py                  # Flask entry point
    rag.py                  # ChromaDB setup and query functions
    state_machine.py        # State management and transition logic
    classifier.py           # Classifier LLM call
    generator.py            # Generator LLM call
    ingest.py               # One-time script: chunk, embed, load ChromaDB
    character.py            # System prompt and character constants
    /data
      art_of_war_giles.txt  # Source text (download from Project Gutenberg)
    .env                    # API keys (never commit)
    requirements.txt

  /frontend
    /src
      App.jsx               # Root component, session management
      ChatInterface.jsx     # Input, message history
      SunziDisplay.jsx      # Sigil, tone-responsive visuals
      TopicGraph.jsx        # Node graph visualization
      StageProgress.jsx     # Stage progress indicator
      ScoreReadout.jsx      # Evaluation score display
    /public
    package.json
```

---

### Key Design Decisions

- **Giles commentary included in RAG corpus** — tagged with `source: "commentary"` metadata. Generation prompt instructs model to use commentary for context only, not as direct speech.
- **Two separate LLM calls per turn** — classifier first (structured output), generator second (free text). These must not be combined.
- **Session state stored server-side** — Flask maintains session state in memory (a dictionary keyed by session_id). No database required for state persistence in local deployment.
- **Weighted vs immediate tone transitions** — see SPEC_STATE_MACHINE.md for full transition rules.
- **Chunk size** — 150-200 words with 20-30 word overlap. See SPEC_RAG.md.

---

### Environment Variables

```
OPENAI_API_KEY=your_key_here
```

Load with `python-dotenv`. Never hardcode. Never commit `.env` to version control.

---

### Spec Documents

| Document | Contents |
|---|---|
| SPEC_RAG.md | ChromaDB setup, chunking, embedding, query flow |
| SPEC_STATE_MACHINE.md | Topics, stages, tones, transition logic, scoring |
| SPEC_LLM_PIPELINE.md | Classifier prompt, generator prompt, RAG insertion |
| SPEC_FRONTEND.md | React components, visual tone states, UI layout |
| SPEC_CHARACTER.md | SUNZI persona, system prompt content, exception handling |