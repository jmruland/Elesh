import os
from flask import Blueprint, request, jsonify, current_app
from query import ask_archivist
from utils.logger import logger

openai_bp = Blueprint("openai_compatible", __name__)

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    index = current_app.config.get("INDEX")
    data = request.get_json()
    model_id = data.get("model", "elesh-archivist")
    user_id = data.get("user", "anonymous")
    # OpenAI format: expects a list of messages
    messages = data.get("messages", [])
    # Custom extension: allow passing 'corpus' parameter
    corpus = data.get("corpus", "both")  # "lore", "rules", or "both"

    if not index:
        logger.warning("OpenAI /chat/completions called but no index available.")
        return jsonify({
            "id": None,
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "The Archivist is not yet connected to the lore archive."
                },
                "finish_reason": "stop"
            }],
            "model": model_id,
        })

    logger.info(f"OpenAI completions: user_id={user_id}, model={model_id}, corpus={corpus}")
    response = ask_archivist(messages, index, user_id=user_id, corpus=corpus)
    
    completion_id = "cmpl-" + os.urandom(6).hex()
    return jsonify({
        "id": completion_id,
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response
            },
            "finish_reason": "stop"
        }],
        "model": model_id,
    })

@openai_bp.route("/v1/models", methods=["GET"])
def models():
    # Expose available models -- simple stub
    return jsonify({
        "object": "list",
        "data": [{
            "id": "elesh-archivist",
            "object": "model",
            "created": 0,
            "owned_by": "Elesh Archivist",
            "permission": [],
            "name": "Elesh Archivist",
            "display_name": "Elesh the Archivist 🧙‍♂️"
        }]
    })