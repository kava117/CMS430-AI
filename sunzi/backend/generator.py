import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from character import GENERATOR_SYSTEM_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FALLBACK_RESPONSE = "INPUT PROCESSING ERROR. RESTATE YOUR RESPONSE."
FALLBACK_EPITAPH = "The record is closed. No annotation was generated."

EPITAPH_SYSTEM_PROMPT = """You are SUNZI. The assessment is over. Write a permanent archival annotation on this subject — 1 to 2 sentences maximum.

Rules:
- Reference something specific from the conversation: a particular answer, a pattern of evasion, a moment of clarity, or its absence.
- Declarative only. No questions. No hedging.
- Cold and archival. This is the permanent record, not a message to the student.
- Do not summarize the whole conversation. Choose one thing that defines this subject.
- Do not use the student's name. Do not use "you."
"""


def format_rag_context(rag_results: list) -> str:
    """Split RAG results by source and format for prompt insertion."""
    if not rag_results:
        return ""

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


def generate_epitaph(conversation_history: list, score: int) -> str:
    """Generate a 1-2 sentence archival annotation on the subject's performance."""
    try:
        history_text = format_history(conversation_history)
        prompt = f"Final score: {score}/100\n\nConversation:\n{history_text}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": EPITAPH_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=80,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Epitaph error: {e}")
        return FALLBACK_EPITAPH


def format_history(history: list) -> str:
    """Format last 6 exchanges (12 turns) for prompt insertion."""
    if not history:
        return ""
    recent = history[-12:]
    lines = []
    for turn in recent:
        label = "STUDENT" if turn["role"] == "user" else "SUNZI"
        lines.append(f"{label}: {turn['content']}")
    return "\n".join(lines)


def generate_response(
    user_input: str,
    state: dict,
    classification: str,
    rag_context: str,
    conversation_history: list
) -> str:
    """
    Generate SUNZI's in-character response given state, classification, RAG context, and history.
    Returns fallback string on API error.
    """
    try:
        history_text = format_history(conversation_history)

        turn_prompt = f"""CURRENT ASSESSMENT STATE:
- Topic: {state['topic']}
- Stage: {state['stage']}
- Tone: {state['tone']}
- Student score: {state['score']}/100
- Student's last classification: {classification}

RETRIEVED PASSAGES:
{rag_context}

CONVERSATION HISTORY:
{history_text}

STUDENT'S CURRENT INPUT:
{user_input}

Before generating your response, read the conversation history. Identify every question or angle you have already raised. Do not repeat or rephrase any of them. If the current stage has been explored from one direction, approach it from a different one — a different passage, a different application, a different demand. Each response must advance the line of examination, not restate it.

Your tone must reflect the current tone state:
- neutral: measured, precise, no affect
- probing: pointed, narrowed questions, increased pressure
- contemptuous: surgical, reference the student's own prior statements as evidence of failure
- illuminated: briefly drop evaluative register, engage with the idea directly, then return
- recalibrating: flag input as outside assessment parameters, restate the last question

Ground your response in the retrieved passages. Prefer Sun Tzu's own words where possible."""

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
    except Exception as e:
        logger.error(f"Generator error: {e}")
        return FALLBACK_RESPONSE
