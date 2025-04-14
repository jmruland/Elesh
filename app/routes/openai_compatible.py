# app/routes/openai_compatible.py

from flask import Blueprint, request, Response, stream_with_context, jsonify
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.settings import Settings
from query import ask_archivist, stream_archivist_response, get_system_prompt
from utils.index_utils import wait_for_ollama, load_or_create_index
from config import VECTORSTORE_DIR, LORE_PATH, MODEL_NAME, OLLAMA_API_BASE_URL
import os, logging, re, uuid, json

openai_bp = Blueprint("openai_compatible", __name__)

# Set the embedding model globally.
Settings.embed_model = OllamaEmbedding(model_name=MODEL_NAME, base_url=OLLAMA_API_BASE_URL)

# Ensure Ollama is ready.
wait_for_ollama()

# Load (or create) the index once.
index = load_or_create_index()
if index:
    logging.info("openai_compatible: Using index from unified loader.")
else:
    logging.error("openai_compatible: Lore index is not available!")

def parse_answer(answer_text):
    pattern = r"Title:\s*(.*?)\s*Answer:\s*(.*)"
    match = re.search(pattern, answer_text, re.DOTALL | re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        content = match.group(2).strip()
    else:
        parts = answer_text.splitlines()
        if len(parts) >= 2 and len(parts[0].split()) <= 10:
            title = parts[0].strip()
            content = "\n".join(parts[1:]).strip()
        else:
            title = ""
            content = answer_text.strip()
    return title, content

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def completions():
    if index is None:
        return jsonify({"error": "Lore index is not available."}), 500

    data = request.get_json()
    question = data["messages"][-1]["content"]
    stream = data.get("stream", False)
    chat_id = f"chatcmpl-{uuid.uuid4().hex}"

    if stream:
        def event_stream():
            first = True
            for chunk in stream_archivist_response(question, index):
                payload = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "choices": [{
                        "delta": {
                            "role": "assistant" if first else None,
                            "content": chunk
                        },
                        "index": 0,
                        "finish_reason": None
                    }],
                    "model": "elesh-archivist"
                }
                yield f"data: {json.dumps(payload)}\n\n"
                first = False
            yield "data: [DONE]\n\n"

        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")
    
    # Fallback to full response (non-streaming)
    raw_answer = ask_archivist(question, index)
    title, content = parse_answer(raw_answer)

    return jsonify({
        "id": chat_id,
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content
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
        "data": [{
            "id": "elesh-archivist",
            "object": "model",
            "created": 0,
            "owned_by": "user",
            "permission": []
        }]
    })