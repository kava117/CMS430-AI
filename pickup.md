# SUNZI — Pickup Notes

## What Has Been Built

All 11 steps from `plan.md` are implemented and committed on branch `chatbot`.

### Backend (`sunzi/backend/`)

| File | Status | Notes |
|---|---|---|
| `character.py` | Complete | `CLASSIFIER_SYSTEM_PROMPT` and `GENERATOR_SYSTEM_PROMPT` constants |
| `state_machine.py` | Complete | Full state/tone/stage/topic logic, 41 tests passing |
| `classifier.py` | Complete | GPT-4o classifier, JSON mode, defaults to `confusion` on error |
| `generator.py` | Complete | `format_rag_context`, `format_history`, `generate_response` |
| `ingest.py` | Complete | Text preprocessing, chunking, OpenAI embedding, ChromaDB ingest |
| `rag.py` | Complete | `query_rag` using OpenAI `text-embedding-3-small` |
| `app.py` | Complete | `/api/turn`, `/api/state/<id>`, `/api/reset` endpoints |
| `requirements.txt` | Complete | flask, flask-cors, openai, chromadb, python-dotenv, pytest, pytest-mock |
| `pytest.ini` | Complete | `testpaths = tests`, `pythonpath = .` |

### Frontend (`sunzi/frontend/`)

| File | Status | Notes |
|---|---|---|
| `src/App.jsx` | Complete | Session ID, gameState, messages, handleSubmit, isLoading |
| `src/App.css` | Complete | CSS variables per tone via `data-tone` attribute on `.app` |
| `src/SunziDisplay.jsx` | Complete | SVG hexagon sigil, 5 tone-reactive CSS animations |
| `src/ChatInterface.jsx` | Complete | Message history, input, submit, loading state |
| `src/TopicGraph.jsx` | Complete | 4-node linear graph with completed/current/upcoming states |
| `src/StageProgress.jsx` | Complete | Segmented 4-stage progress indicator |
| `src/ScoreReadout.jsx` | Complete | Animated progress bar for score |
| `vite.config.js` | Complete | API proxy to `http://localhost:5000`, Vitest config with jsdom |
| `package.json` | Complete | react, vitest, @testing-library/react, @testing-library/user-event |
| `src/test-setup.js` | Complete | jest-dom import + `scrollIntoView` mock for jsdom |

### Tests

- **Backend:** 108 tests passing (`pytest tests/ --ignore=tests/test_rag.py`)
- **Frontend:** 56 tests passing (`npm test`)
- **RAG query tests** (4 tests in `test_rag.py`): skipped with `pytest.skip` until ChromaDB is populated

---

## What Still Needs To Be Done

### 1. Run `ingest.py` (BLOCKING — must do first)

The ChromaDB vector store has never been populated. This is required for the app to work.

**Root cause of prior failures:** The `.env` file at `sunzi/backend/.env` had an invalid/expired OpenAI API key (401 errors). The user needs to put a valid key there.

```bash
# Verify the key works first:
cd sunzi/backend
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); c = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print(c.models.list().data[0].id)"

# Then run ingest:
python ingest.py
```

Ingest will embed 699 chunks (403 sun_tzu + 296 commentary) using `text-embedding-3-small`. Takes ~2 minutes. Writes to `sunzi/backend/chroma_db/`.

After ingest, run the full RAG test suite to confirm:
```bash
pytest tests/test_rag.py -v
```

All 4 previously-skipped query tests should pass.

### 2. Run the App End-to-End

Once ingest is done:

```bash
# Terminal 1 — Flask backend
cd sunzi/backend
python app.py
# Runs on http://localhost:5000

# Terminal 2 — React frontend
cd sunzi/frontend
npm run dev
# Runs on http://localhost:5173, proxies /api/* to Flask
```

Open `http://localhost:5173` and verify the UI renders and a conversation works.

### 3. Verify the Opening Message

Currently `App.jsx` has no opening message from SUNZI — the chat starts empty. The spec implies SUNZI should open the assessment. Two options:

**Option A (preferred):** Add a `POST /api/start` endpoint that returns SUNZI's opening line without requiring user input. Call it from `useEffect` in `App.jsx` on mount.

**Option B:** Add a hardcoded opening message to the initial `messages` state in `App.jsx`.

Option A is more in-character (SUNZI generates the opening via the LLM). This was noted in Step 11 of `plan.md` but not implemented.

### 4. Minor: `index.css` Still Has Vite Defaults

`sunzi/frontend/src/index.css` still contains Vite's default boilerplate styles (body centering, `#root` styles, etc.). These conflict slightly with the dark terminal aesthetic. Replace with minimal base styles:

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0A0A0F; color: #C8C8D0; font-family: 'Courier New', monospace; }
#root { min-height: 100vh; }
```

### 5. Important Implementation Note: Embedding Model Change

The spec called for `sentence-transformers` / `all-MiniLM-L6-v2`. This was changed to **OpenAI `text-embedding-3-small`** because HuggingFace downloads are blocked in this environment (403 Forbidden).

- `ingest.py` now calls `openai.embeddings.create()` in batches of 100
- `rag.py` now calls `openai.embeddings.create()` for query-time embedding
- `sentence-transformers` and `torch` have been removed from `requirements.txt`

This is functionally equivalent — same cosine similarity search in ChromaDB, just a different embedding provider.

---

## How to Run Tests

```bash
# Backend
cd sunzi/backend
pytest tests/ -v                        # all tests (4 RAG query tests skip if no chroma_db)
pytest tests/ -v --ignore=tests/test_rag.py   # 108 tests, no external deps

# Frontend
cd sunzi/frontend
npm test                                # 56 tests
```

---

## Key Architecture Reminders

- **Two LLM calls per turn:** classifier first (temp=0, max_tokens=50, JSON mode), then generator (temp=0.7, max_tokens=300). Never combined.
- **State is server-side:** `StateMachine.sessions` dict keyed by `session_id`. No DB.
- **Tone transitions:** `illuminated` decays after 1 turn; `recalibrating` remembers previous tone in `_prev_tone` (internal key, stripped from public state).
- **Stage advance condition:** `stage_turn_count >= 2` AND classification in `{understanding, insight}`.
- **Patch targets in tests:** `app.classify_input` and `app.generate_response` (not `classifier.classify_input`) because `app.py` imports them directly with `from ... import`.
