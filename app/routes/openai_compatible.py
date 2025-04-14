# app/routes/openai_compatible.py

from flask import Blueprint, request, Response, stream_with_context, jsonify
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.settings import Settings
from query import ask_archivist, stream_archivist_response, get_system_prompt
from utils.index_utils import wait_for_ollama, load_or_create_index
from config import VECTORSTORE_DIR, LORE_PATH, MODEL_NAME, OLLAMA_API_BASE_URL
import os

openai_bp = Blueprint("openai_compatible", __name__)

# Set embed model globally
Settings.embed_model = OllamaEmbedding(model_name=MODEL_NAME, base_url=OLLAMA_API_BASE_URL)

# Ensure Ollama is up
wait_for_ollama()

# Use our unified index-loading function
index = load_or_create_index()
if index:
    print("[INFO] Using index from unified loader.")
else:
    print("[ERROR] Lore index is not available!")

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def completions():
    if index is None:
        return jsonify({"error": "Lore index is not available."}), 500

    data = request.get_json()
    question = data["messages"][-1]["content"]
    stream = data.get("stream", False)

    if stream:
        def event_stream():
            for chunk in stream_archivist_response(question, index):
                yield f"data: {chunk}\n\n"
        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

    answer = ask_archivist(question, index)
    return jsonify({
        "id": "chatcmpl-local",
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": answer
            },
            "finish_reason": "stop"
        }],
        "model": "elesh-archivist",
        "system_prompt": get_system_prompt()
    })

@openai_bp.route("/v1/models", methods=["GET"])
def models():
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": "elesh-archivist",
                "object": "model",
                "created": 0,
                "owned_by": "user",
                "permission": []
            }
        ]
    })