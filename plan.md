# SUNZI — Implementation Plan

**Stack:** Flask + React (Vite) + ChromaDB + sentence-transformers + OpenAI GPT-4o
**Test frameworks:** pytest (backend), Vitest + React Testing Library (frontend)

---

## Step 1 — Project Scaffolding

Create the full directory structure, dependency files, and verify the environment.

**Deliverables:**
- `sunzi/backend/` directory with `app.py`, `requirements.txt`, `.env.example`, `character.py`
- `sunzi/frontend/` directory with Vite React scaffold, `package.json`, `vite.config.js`
- `.gitignore` covering `.env`, `chroma_db/`, `node_modules/`, `__pycache__/`
- `backend/data/art_of_war_giles.txt` (copied from repo root)

**`requirements.txt`:**
```
flask
flask-cors
openai
chromadb
sentence-transformers
torch
python-dotenv
pytest
pytest-mock
```

**`vite.config.js`:**
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://localhost:5000' }
  }
})
```

**Tests (`backend/tests/test_scaffold.py`):**
- All required backend files exist
- `requirements.txt` contains expected packages
- `.env.example` contains `OPENAI_API_KEY` placeholder
- `art_of_war_giles.txt` is present and non-empty (> 10,000 characters)
- `character.py` exports `GENERATOR_SYSTEM_PROMPT` and `CLASSIFIER_SYSTEM_PROMPT` as non-empty strings

**Run:** `cd sunzi/backend && pytest tests/test_scaffold.py -v`

---

## Step 2 — RAG: Ingest Pipeline (`ingest.py`, `rag.py`)

Build the text preprocessing, chunking, embedding, and ChromaDB ingestion pipeline.

**Deliverables:**
- `backend/ingest.py` — one-time script: load text → preprocess → chunk → embed → store
- `backend/rag.py` — exposes `query_rag(topic, stage, user_input, n_results=5) -> list[dict]`
- `backend/chroma_db/` — populated ChromaDB collection after running ingest

**Key functions to implement:**

`ingest.py`:
- `strip_gutenberg_boilerplate(text: str) -> str` — remove header/footer
- `parse_sections(text: str) -> list[dict]` — split into `{text, source, chapter, chapter_title}` sections tagging sun_tzu vs commentary
- `chunk_text(text: str, chunk_size=175, overlap=25) -> list[str]` — sliding window, no mid-sentence splits
- `run_ingest()` — orchestrates full pipeline, prints summary (total chunks, sun_tzu count, commentary count)

`rag.py`:
- `get_collection()` — returns ChromaDB collection (persistent client)
- `query_rag(topic, stage, user_input, n_results=5) -> list[dict]` — builds query string, encodes, queries, returns list of `{text, source, chapter, chapter_title}`

**Tests (`backend/tests/test_rag.py`):**
- `strip_gutenberg_boilerplate`: output does not contain "Project Gutenberg" in first/last 200 chars
- `parse_sections`: returns list of dicts with required keys; all items have `source` in `{"sun_tzu", "commentary"}`; all items have `chapter` as int 1–13
- `chunk_text`: all chunks are between 100–250 words; no chunk ends mid-sentence (ends with `.`, `?`, or `!`); consecutive chunks share ~25-word overlap
- `chunk_text`: handles short input (< chunk_size) without error — returns single chunk
- `query_rag` (requires ingest to have been run): returns list of 5 dicts; each dict has keys `text`, `source`, `chapter`, `chapter_title`; results are non-empty strings
- `query_rag`: different topic/stage/input combinations return different top results (not identical)

**Run:**
```bash
cd sunzi/backend && python ingest.py   # one-time
pytest tests/test_rag.py -v
```

---

## Step 3 — State Machine (`state_machine.py`)

Implement the full state management and transition logic. This step has no LLM dependency and should be thoroughly tested.

**Deliverables:**
- `backend/state_machine.py` — `StateMachine` class with `get_state`, `process_turn`, `reset`

**Initial state:**
```python
{
    "topic": "deception", "stage": "introduction", "tone": "neutral",
    "score": 50, "stage_turn_count": 0, "tone_signal_count": 0,
    "topic_index": 0, "conversation_complete": False
}
```

**Tests (`backend/tests/test_state_machine.py`):**

*Initialization:*
- New session returns correct initial state
- Two calls to `get_state` with same session_id return same object
- Different session_ids get independent states
- `reset` returns state to initial values

*Scoring:*
- `insight` adds +10 to score
- `understanding` adds +5
- `clarification` adds +0
- `confusion` subtracts 3
- `evasion` subtracts 5
- `off_topic` subtracts 7
- Score clamps at 100 (no overflow)
- Score clamps at 0 (no underflow)

*Tone transitions — immediate:*
- `insight` from `neutral` → `illuminated` immediately
- `insight` from `probing` → `illuminated` immediately
- `insight` from `contemptuous` → `illuminated` immediately (special case)
- `off_topic` from `neutral` → `recalibrating` immediately
- `off_topic` from `probing` → `recalibrating` immediately
- `illuminated` decays to `neutral` on the NEXT turn (not immediately)
- `recalibrating` returns to previous tone once student re-engages (non-off_topic signal)

*Tone transitions — weighted (2 consecutive signals):*
- 1x `confusion` from `neutral` → still `neutral` (no transition yet)
- 2x `confusion` from `neutral` → `probing`
- 1x `evasion` + 1x `confusion` from `neutral` → `probing` (mixed signals count)
- 2x `confusion` from `probing` → `contemptuous`
- 1x `understanding` from `probing` resets signal count (no transition)
- 2x `understanding` from `probing` → `neutral`
- 2x `understanding` from `contemptuous` → `neutral`
- Non-matching signal resets `tone_signal_count` to 0

*Stage advancement:*
- `stage_turn_count` increments each turn
- Stage does NOT advance with `understanding` on turn 1 (count < 2)
- Stage advances from `introduction` → `examination` on `understanding` with `stage_turn_count >= 2`
- Stage advances on `insight` with `stage_turn_count >= 2`
- Stage does NOT advance on `confusion` even with `stage_turn_count >= 2`
- Stage does NOT advance on `evasion` even with `stage_turn_count >= 2`
- `stage_turn_count` resets to 0 on stage advance
- Full stage traversal: introduction → examination → challenge → resolution

*Topic advancement:*
- After resolution completes, `topic_index` increments and `stage` resets to `introduction`
- Topic sequence: deception → self_knowledge → adaptability → victory
- After victory/resolution completes, `conversation_complete` is set to `True`
- No further state changes occur once `conversation_complete` is `True`

**Run:** `cd sunzi/backend && pytest tests/test_state_machine.py -v`

---

## Step 4 — Classifier (`classifier.py`)

Implement the LLM classifier call with mocked tests (no real API calls in tests).

**Deliverables:**
- `backend/classifier.py` — `classify_input(user_input, current_topic, current_stage) -> str`

**Tests (`backend/tests/test_classifier.py`):**

All tests use `pytest-mock` to patch `openai.OpenAI` — no real API calls.

- Mock returns valid JSON `{"classification": "understanding"}` → function returns `"understanding"`
- Mock returns each of the 6 valid classifications → all return correctly
- Mock returns JSON with unknown value `{"classification": "brilliant"}` → returns `"confusion"` (default)
- Mock returns malformed JSON → returns `"confusion"` (default)
- Mock returns empty response → returns `"confusion"` (default)
- API call is made with `model="gpt-4o"`, `temperature=0`, `max_tokens=50`
- API call messages include `current_topic` and `current_stage` in user message content
- API call uses `response_format={"type": "json_object"}`

**Run:** `cd sunzi/backend && pytest tests/test_classifier.py -v`

---

## Step 5 — Generator (`generator.py`)

Implement the RAG context formatter, history formatter, and generator LLM call.

**Deliverables:**
- `backend/generator.py` — `format_rag_context`, `format_history`, `generate_response`

**Tests (`backend/tests/test_generator.py`):**

*`format_rag_context`:*
- Empty list → returns empty string
- List with only `sun_tzu` chunks → output contains "SUN TZU'S WORDS" header, no "SCHOLARLY CONTEXT" header
- List with only `commentary` chunks → output contains "SCHOLARLY CONTEXT" header, no "SUN TZU'S WORDS" header
- Mixed list → output contains both headers in correct order (sun_tzu first)
- Chapter number and title appear in sun_tzu section: `[Chapter 1: Laying Plans]`
- Commentary text appears without chapter attribution

*`format_history`:*
- Empty history → returns empty string
- Single user turn → returns `"STUDENT: ..."` line
- Single sunzi turn → returns `"SUNZI: ..."` line
- History longer than 12 items → only last 12 returned (6 exchanges)
- History of exactly 12 → all 12 returned
- Labels are `STUDENT` and `SUNZI` (not `user`/`assistant`)

*`generate_response` (mocked API):*
- Returns the string content from the mock response
- API call uses `model="gpt-4o"`, `temperature=0.7`, `max_tokens=300`
- Turn prompt includes topic, stage, tone, score, classification
- Turn prompt includes RAG context
- System prompt is `GENERATOR_SYSTEM_PROMPT` from `character.py`
- API failure → returns `"INPUT PROCESSING ERROR. RESTATE YOUR RESPONSE."`

**Run:** `cd sunzi/backend && pytest tests/test_generator.py -v`

---

## Step 6 — Flask App (`app.py`)

Wire the full pipeline into Flask endpoints. Tests mock the LLM calls.

**Deliverables:**
- `backend/app.py` — Flask app with `/api/turn`, `/api/state/<session_id>`, `/api/reset`
- CORS configured for local development

**Tests (`backend/tests/test_app.py`):**

Setup: Flask test client, patch `classifier.classify_input` and `generator.generate_response` at module level.

*`POST /api/turn`:*
- Returns 200 with JSON containing `response_text`, `state`, `classification`
- `state` contains all 8 required keys
- `classification` is one of the 6 valid values
- Missing `user_input` → returns 400
- Missing `session_id` → returns 400
- Consecutive turns with same `session_id` → `stage_turn_count` increments
- Different `session_id` → independent state (turn count stays at 0)
- Mocked classifier returning `"insight"` → response `state.tone` is `"illuminated"`
- Mocked classifier returning `"off_topic"` → response `state.tone` is `"recalibrating"`
- When LLM raises exception → response contains fallback error string

*`GET /api/state/<session_id>`:*
- Unknown session_id → returns initial state (200, not 404)
- Known session_id after one turn → returns updated state

*`POST /api/reset`:*
- After turns, reset returns state to initial values
- Subsequent `GET /api/state` returns initial state

*Conversation history:*
- After 2 turns, history stored server-side has 4 entries (2 user + 2 sunzi)
- Generator is called with non-empty history on turn 2

**Run:** `cd sunzi/backend && pytest tests/test_app.py -v`

---

## Step 7 — Frontend Scaffold + `App.jsx`

Initialize the Vite React project and implement the root component with session management and API integration.

**Deliverables:**
- `sunzi/frontend/` — Vite React app (`npm create vite@latest`)
- `src/App.jsx` — session ID, game state, messages, `handleSubmit`, loading state
- `src/App.css` — base layout and CSS variables for tone colors
- Vitest + React Testing Library configured in `package.json` / `vite.config.js`

**Frontend test setup (`package.json` devDependencies):**
```json
"vitest": "^1.0.0",
"@vitest/ui": "^1.0.0",
"@testing-library/react": "^14.0.0",
"@testing-library/user-event": "^14.0.0",
"jsdom": "^24.0.0"
```

**Tests (`src/__tests__/App.test.jsx`):**
- App renders without crashing
- `sessionId` is generated on mount (non-empty string in component state)
- Two mounts generate different session IDs
- Initial `gameState` matches the spec's initial state shape (all 8 keys present)
- Initial `messages` is an empty array
- Initial `isLoading` is false
- `handleSubmit` sets `isLoading` to true during fetch (mock fetch)
- After successful fetch, `gameState` is updated from response `state`
- After successful fetch, `messages` has 2 new entries (user + sunzi)
- After successful fetch, `isLoading` is false
- Fetch called with correct URL `/api/turn` and body `{user_input, session_id}`

**Run:** `cd sunzi/frontend && npm test`

---

## Step 8 — `SunziDisplay.jsx`

The central animated sigil component with tone-reactive CSS animations.

**Deliverables:**
- `src/SunziDisplay.jsx` — SVG hexagon sigil with radiating lines
- `src/SunziDisplay.css` — keyframe animations for all 5 tone states
- Tone label display below sigil: `TONE STATE: EVALUATING`

**Animation classes:**
| Tone | Class | Behavior |
|---|---|---|
| `neutral` | `pulse-slow` | 3s pulse loop |
| `probing` | `pulse-fast` | 1.5s pulse + slight rotation |
| `contemptuous` | `still` | No animation |
| `illuminated` | `flare` | One-shot expand + fade, then neutral |
| `recalibrating` | `glitch` | Irregular opacity flicker |

**Tests (`src/__tests__/SunziDisplay.test.jsx`):**
- Renders without crashing for each of the 5 tone values
- SVG element is present in the DOM
- Each tone applies the correct CSS animation class to the sigil element
- Tone label is visible in the DOM (e.g., "TONE STATE: NEUTRAL")
- `illuminated` tone label reads "TONE STATE: ILLUMINATED"
- `recalibrating` tone label reads "TONE STATE: RECALIBRATING"
- Color prop/CSS variable matches spec values per tone (neutral → `#4A9EFF`, etc.)
- Invalid/undefined tone prop → renders without crashing (falls back to neutral)

**Run:** `cd sunzi/frontend && npm test`

---

## Step 9 — `ChatInterface.jsx`

Message history display and user input component.

**Deliverables:**
- `src/ChatInterface.jsx` — message list, input field, submit button
- `src/ChatInterface.css` — dark terminal styling, tone-colored border

**Tests (`src/__tests__/ChatInterface.test.jsx`):**
- Renders with empty messages — no message elements in DOM
- SUNZI messages render with prefix `> SUNZI:`
- User messages render with prefix `> YOU:`
- Input field is present and accepts text
- Clicking submit calls `onSubmit` with input value
- Pressing Enter calls `onSubmit` with input value
- After submit, input field is cleared
- `isLoading=true` disables the input and submit button
- `isLoading=true` displays `PROCESSING INPUT...` text
- `isLoading=false` removes loading text and re-enables input
- Multiple messages render in correct order (oldest first)
- `onSubmit` is NOT called when input is empty

**Run:** `cd sunzi/frontend && npm test`

---

## Step 10 — `TopicGraph.jsx`, `StageProgress.jsx`, `ScoreReadout.jsx`

The three status/progress display components.

**Deliverables:**
- `src/TopicGraph.jsx`
- `src/StageProgress.jsx`
- `src/ScoreReadout.jsx`
- Styles inline or in component CSS files

**Tests (`src/__tests__/StatusComponents.test.jsx`):**

*TopicGraph:*
- Renders 4 topic nodes
- All 4 topic names appear in the DOM (DECEPTION, SELF-KNOWLEDGE, ADAPTABILITY, VICTORY)
- `topicIndex=0` → first node has "current" styling, others are "upcoming"
- `topicIndex=2` → first two nodes have "completed" styling, third is "current", fourth "upcoming"
- Current stage label appears below the current node
- `topicIndex=3` with stage `resolution` → last node is "current"

*StageProgress:*
- Renders 4 stage segments
- All 4 stage names appear: INTRO, EXAM, CHALLENGE, RESOLUTION
- `stage="introduction"` → first segment highlighted, rest dim
- `stage="examination"` → first segment completed, second highlighted
- `stage="challenge"` → first two completed, third highlighted
- `stage="resolution"` → first three completed, fourth highlighted

*ScoreReadout:*
- Renders the label `HUMAN INTELLIGENCE ASSESSMENT`
- `score=50` → progress bar width is approximately 50%
- `score=0` → bar width is 0%
- `score=100` → bar width is 100%
- Score value is displayed as text (e.g., "50%")
- `score=75` → bar width is approximately 75%

**Run:** `cd sunzi/frontend && npm test`

---

## Step 11 — Full Integration

Wire all frontend components together in App.jsx, connect to live backend, and verify end-to-end flow.

**Deliverables:**
- `App.jsx` updated to render all 5 components with correct props
- All tone-color CSS variables applied globally from `gameState.tone`
- SUNZI's opening message sent automatically on session start (call `/api/turn` with `user_input=""` or a dedicated `/api/start` endpoint)
- `sunzi/README.md` with setup and run instructions

**Integration Tests (`backend/tests/test_integration.py`):**

Uses Flask test client with **mocked OpenAI** (no real API calls). Runs the full pipeline end-to-end through the Flask app.

- Full turn: POST `/api/turn` → classifier mock returns `"understanding"` → state machine updates → generator mock returns string → response JSON is valid
- Score accumulates correctly over 3 mocked turns with known classifications
- 2 consecutive mocked `confusion` classifications → `state.tone` becomes `"probing"` by turn 2
- Mocked `insight` classification → `state.tone` becomes `"illuminated"`
- `stage_turn_count >= 2` + mocked `understanding` → stage advances in response state
- `POST /api/reset` then `GET /api/state` → returns clean initial state
- History grows with each turn: after 3 turns, generator receives history with 6 entries

**Frontend smoke test (`src/__tests__/App.integration.test.jsx`):**

Uses `msw` (Mock Service Worker) to intercept `/api/turn` at the network level.

- App renders all 5 child components on mount
- Submitting a message shows user message and SUNZI response in chat
- State-driven components (TopicGraph, ScoreReadout, StageProgress) update after a turn
- SunziDisplay updates tone class when mock API returns a different tone

**Run:**
```bash
cd sunzi/backend && pytest tests/test_integration.py -v
cd sunzi/frontend && npm test
```

---

## Test Count Summary

| Step | File | Approx Tests |
|---|---|---|
| 1 | test_scaffold.py | 5 |
| 2 | test_rag.py | 8 |
| 3 | test_state_machine.py | 30 |
| 4 | test_classifier.py | 8 |
| 5 | test_generator.py | 14 |
| 6 | test_app.py | 16 |
| 7 | App.test.jsx | 10 |
| 8 | SunziDisplay.test.jsx | 8 |
| 9 | ChatInterface.test.jsx | 11 |
| 10 | StatusComponents.test.jsx | 16 |
| 11 | test_integration.py + App.integration.test.jsx | 14 |
| **Total** | | **~140** |
