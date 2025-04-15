from flask import Blueprint, request, jsonify, current_app
from query import ask_archivist
from utils.logger import logger

ask_bp = Blueprint("ask", __name__)

@ask_bp.route("/ask", methods=["POST"])
def ask():
    index = current_app.config.get("INDEX")
    data = request.get_json()
    question = data.get("question", "")
    corpus = data.get("corpus", "both")  # Can be "lore", "rules", or "both"
    user_id = data.get("user", "anonymous")  # For logging/auditing if wanted

    if not index:
        logger.warning("Ask endpoint called but no index available.")
        return jsonify({"response": "The Archivist is not yet connected to the lore archive."})

    # Support simple alternates: if the user sends messages array (OpenAI style)
    messages = data.get("messages")
    if not messages:
        messages = [{"role": "user", "content": question}]
    logger.info(f"API /ask: user_id={user_id}, corpus={corpus}, question='{question[:80]}'")

    response = ask_archivist(messages, index, user_id=user_id, corpus=corpus)
    return jsonify({"response": response})