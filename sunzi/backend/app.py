from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from state_machine import StateMachine
from classifier import classify_input
from generator import generate_response, format_rag_context

load_dotenv()

app = Flask(__name__)
CORS(app)

state_machine = StateMachine()
session_histories: dict[str, list] = {}


def _get_rag_results(topic, stage, user_input):
    """Query RAG if available; return empty list if not ingested yet."""
    try:
        from rag import query_rag
        return query_rag(topic, stage, user_input)
    except Exception:
        return []


@app.route('/api/turn', methods=['POST'])
def handle_turn():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    if "user_input" not in data:
        return jsonify({"error": "Missing user_input"}), 400
    if "session_id" not in data:
        return jsonify({"error": "Missing session_id"}), 400

    user_input = data["user_input"]
    session_id = data["session_id"]

    # 1. Get current state (before classification)
    state = state_machine.get_state(session_id)

    # 2. Classify input
    classification = classify_input(user_input, state["topic"], state["stage"])

    # 3. Update state based on classification
    state = state_machine.process_turn(session_id, classification)

    # 4. Query RAG
    rag_results = _get_rag_results(state["topic"], state["stage"], user_input)
    rag_context = format_rag_context(rag_results)

    # 5. Get conversation history
    history = session_histories.get(session_id, [])

    # 6. Generate response
    response_text = generate_response(user_input, state, classification, rag_context, history)

    # 7. Update history
    history = list(history)
    history.append({"role": "user", "content": user_input})
    history.append({"role": "sunzi", "content": response_text})
    session_histories[session_id] = history

    return jsonify({
        "response_text": response_text,
        "state": state,
        "classification": classification
    })


@app.route('/api/state/<session_id>', methods=['GET'])
def get_state(session_id):
    state = state_machine.get_state(session_id)
    return jsonify(state)


@app.route('/api/start', methods=['POST'])
def start():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "default")

    # Reset to a clean state for this session
    state = state_machine.reset(session_id)
    session_histories[session_id] = []

    # Generate SUNZI's opening line without any user input
    rag_results = _get_rag_results(state["topic"], state["stage"], "")
    rag_context = format_rag_context(rag_results)
    opening_prompt = "BEGIN THE ASSESSMENT. Deliver your opening statement to the student."
    response_text = generate_response(opening_prompt, state, "neutral", rag_context, [])

    session_histories[session_id] = [{"role": "sunzi", "content": response_text}]

    return jsonify({
        "response_text": response_text,
        "state": state,
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "default")
    state = state_machine.reset(session_id)
    session_histories[session_id] = []
    return jsonify(state)


if __name__ == '__main__':
    app.run(debug=True)
