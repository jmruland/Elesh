from flask import Blueprint, request, jsonify, current_app
from query import ask_archivist

openai_bp = Blueprint("openai_compatible", __name__)

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def completions():
    index = current_app.config.get("INDEX")
    data = request.get_json()
    messages = data.get("messages", [])

    if not messages or not isinstance(messages, list):
        return jsonify({"error": "Invalid request: 'messages' must be a list."}), 400

    question = "\n\n".join([msg.get("content", "") for msg in messages if msg.get("role") == "user"])

    if not index:
        return jsonify({
            "choices": [{"message": {"role": "assistant", "content": "The Archivist is not connected to the lore archive."}}]
        })

    answer = ask_archivist(question, index)
    return jsonify({
        "choices": [{"message": {"role": "assistant", "content": answer}}]
    })