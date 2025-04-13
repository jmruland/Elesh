from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
from query import ask_archivist

openai_bp = Blueprint("openai_compatible", __name__)

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def completions():
    index = current_app.config.get("INDEX")
    data = request.get_json()
    messages = data.get("messages", [])
    stream = data.get("stream", False)

    if not messages or not isinstance(messages, list):
        return jsonify({"error": "Invalid request: 'messages' must be a list."}), 400

    question = "\n\n".join([msg.get("content", "") for msg in messages if msg.get("role") == "user"])

    if not index:
        return jsonify({
            "choices": [{"message": {"role": "assistant", "content": "The Archivist is not connected to the lore archive."}}]
        })

    if not stream:
        answer = ask_archivist(question, index)
        return jsonify({
            "choices": [{"message": {"role": "assistant", "content": answer}}]
        })

    def generate():
        answer = ask_archivist(question, index)
        for word in answer.split():
            yield f"data: {{\"choices\":[{{\"delta\":{{\"content\":\"{word} \"}}}}]}}\n"
        yield "data: [DONE]\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")