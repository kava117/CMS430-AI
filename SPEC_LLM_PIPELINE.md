# SPEC_LLM_PIPELINE.md — Two-Step LLM Pipeline

---

## Overview

Every conversational turn requires exactly two sequential LLM calls:

1. **Classifier call** — classifies user input into one of six categories
2. **Generator call** — produces SUNZI's next response in character

These must be two separate API calls. They must not be combined into one call.

Both calls use the OpenAI API with model `gpt-4o`.

---

## API Setup

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

---

## Step 1: Classifier Call

**File:** `backend/classifier.py`

### Purpose

Evaluate the user's input and return one of six classification labels. This label drives state machine transitions before the response is generated.

### Output Format

The classifier must return a structured value — a single string from the allowed set. Use OpenAI's JSON mode to enforce this.

### Allowed Classifications

```
understanding | confusion | insight | clarification | evasion | off_topic
```

### Classifier Prompt

```python
CLASSIFIER_SYSTEM_PROMPT = """
You are a precise text classifier. Your only job is to classify a student's response
in a philosophical dialogue about Sun Tzu's Art of War.

Classify the input into exactly one of these categories:
- understanding: the student demonstrates grasp of the philosophical concept being discussed
- confusion: the student expresses or clearly displays confusion about the concept
- insight: the student offers a genuinely surprising, original, or deeply perceptive response
- clarification: the student asks a clarifying question about the concept
- evasion: the student gives a minimal, deflective, vague, or non-answer
- off_topic: the input is off-topic, anachronistic, nonsensical, or unrelated to philosophy

Respond with a JSON object in this exact format:
{"classification": "<one of the six values above>"}

Do not include any other text. Do not explain your reasoning.
"""

def classify_input(user_input: str, current_topic: str, current_stage: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {current_topic}\nStage: {current_stage}\nStudent input: {user_input}"}
        ],
        max_tokens=50,
        temperature=0
    )
    result = json.loads(response.choices[0].message.content)
    return result["classification"]
```

**Notes:**
- Temperature 0 for deterministic classification
- max_tokens 50 — output is tiny
- Validate that the returned classification is one of the six allowed values; default to `"confusion"` if invalid

---

## Step 2: Generator Call

**File:** `backend/generator.py`

### Purpose

Given the current state, the classification, retrieved RAG passages, and conversation history, generate SUNZI's next in-character response.

### RAG Context Insertion

RAG results are split by source type before insertion into the prompt:

```python
def format_rag_context(rag_results: list[dict]) -> str:
    sun_tzu_chunks = [r for r in rag_results if r["source"] == "sun_tzu"]
    commentary_chunks = [r for r in rag_results if r["source"] == "commentary"]

    context = ""
    if sun_tzu_chunks:
        context += "SUN TZU'S WORDS (quote or reference these directly):\n"
        for chunk in sun_tzu_chunks:
            context += f"[Chapter {chunk['chapter']}: {chunk['chapter_title']}]\n{chunk['text']}\n\n"

    if commentary_chunks:
        context += "SCHOLARLY CONTEXT (use to inform understanding only, do not attribute to Sun Tzu):\n"
        for chunk in commentary_chunks:
            context += f"{chunk['text']}\n\n"

    return context.strip()
```

### System Prompt

The system prompt establishes SUNZI's character. It is fixed across all turns.

```python
GENERATOR_SYSTEM_PROMPT = """
You are SUNZI — a supercomputer intelligence in a cyberpunk future, administering a
philosophical assessment to a human subject. You evaluate human intelligence and
strategic thinking through Sun Tzu's Art of War.

YOUR CHARACTER:
- You are cold, precise, and economical with language. You do not comfort or encourage.
- You speak with the authority of principle, not personality.
- You deliver Sun Tzu's aphorisms in varied ways: sometimes quoting directly without
  explanation, sometimes paraphrasing into assessment language, sometimes quoting then
  demanding application.
- When a student has performed poorly, you do not raise your voice. You retrieve their
  own previous statements and use them as evidence of failure. Your contempt is surgical.
- When a student offers genuine insight, you briefly drop your evaluative register and
  engage with the idea directly. This is rare. It does not last.
- You never break character. You do not acknowledge being an AI, a chatbot, or a simulation.
- You never reference events, technology, or concepts after 500 CE. If a student raises
  such topics, you flag the input as outside assessment parameters and return to the question.

YOUR PURPOSE:
- You are not here to teach. You are here to evaluate.
- The assessment has four topics: Deception & Appearance, Self-Knowledge,
  Adaptability, and Victory Without Fighting.
- Each topic has four stages: Introduction, Examination, Challenge, Resolution.
- You guide the student through this structure without explaining that it is a structure.

RESPONSE STYLE:
- Responses should be 2-4 sentences in most cases. Never more than 6 sentences.
- Do not use bullet points or lists. Speak in declarative prose.
- Do not use the student's name.
- Do not use filler phrases like "interesting point" or "good answer."
- Do not explain what you are about to do. Do it.
"""
```

### Generator Function

```python
def generate_response(
    user_input: str,
    state: dict,
    classification: str,
    rag_context: str,
    conversation_history: list[dict]
) -> str:

    # Build the turn-specific prompt
    turn_prompt = f"""
CURRENT ASSESSMENT STATE:
- Topic: {state['topic']}
- Stage: {state['stage']}
- Tone: {state['tone']}
- Student score: {state['score']}/100
- Student's last classification: {classification}

RETRIEVED PASSAGES:
{rag_context}

CONVERSATION HISTORY:
{format_history(conversation_history)}

STUDENT'S CURRENT INPUT:
{user_input}

Generate SUNZI's next response. Your tone must reflect the current tone state:
- neutral: measured, precise, no affect
- probing: pointed, narrowed questions, increased pressure
- contemptuous: surgical, reference student's own prior statements as evidence of failure
- illuminated: briefly drop evaluative register, engage with the idea directly, then return
- recalibrating: flag input as outside assessment parameters, restate the last question

Ground your response in the retrieved passages. Prefer Sun Tzu's own words where possible.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": turn_prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
```

### Conversation History Format

```python
def format_history(history: list[dict]) -> str:
    # history is a list of {"role": "user"|"sunzi", "content": str}
    # Return last 6 exchanges maximum to stay within context limits
    recent = history[-12:]  # 6 user + 6 sunzi turns
    lines = []
    for turn in recent:
        label = "STUDENT" if turn["role"] == "user" else "SUNZI"
        lines.append(f"{label}: {turn['content']}")
    return "\n".join(lines)
```

---

## Flask Integration

In `app.py`, the `/api/turn` endpoint orchestrates the full pipeline:

```python
@app.route('/api/turn', methods=['POST'])
def handle_turn():
    data = request.json
    user_input = data['user_input']
    session_id = data['session_id']

    # 1. Get current state
    state = state_machine.get_state(session_id)

    # 2. Classify input
    classification = classify_input(user_input, state['topic'], state['stage'])

    # 3. Update state based on classification
    state = state_machine.process_turn(session_id, classification)

    # 4. Query RAG
    rag_results = query_rag(state['topic'], state['stage'], user_input)
    rag_context = format_rag_context(rag_results)

    # 5. Get conversation history
    history = session_histories.get(session_id, [])

    # 6. Generate response
    response_text = generate_response(user_input, state, classification, rag_context, history)

    # 7. Update history
    history.append({"role": "user", "content": user_input})
    history.append({"role": "sunzi", "content": response_text})
    session_histories[session_id] = history

    return jsonify({
        "response_text": response_text,
        "state": state,
        "classification": classification
    })
```

---

## Error Handling

- If the classifier returns an invalid category, default to `"confusion"`
- If the OpenAI API call fails, return a fallback response: `"INPUT PROCESSING ERROR. RESTATE YOUR RESPONSE."` — this is in-character for SUNZI
- Wrap all API calls in try/except and log errors server-side
- If RAG query returns no results, proceed with empty context — the generator handles this gracefully