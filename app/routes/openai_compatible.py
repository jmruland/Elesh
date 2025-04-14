# app/routes/openai_compatible.py

from flask import Blueprint, request, Response, stream_with_context, jsonify
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.settings import Settings
from query import ask_archivist, stream_archivist_response, get_system_prompt
from utils.index_utils import wait_for_ollama, load_or_create_index
from config import MODEL_NAME, OLLAMA_API_BASE_URL
from utils.db import init_db
import logging
import json
import uuid

openai_bp = Blueprint("openai_compatible", __name__)

# One-time setup
Settings.embed_model = OllamaEmbedding(model_name=MODEL_NAME, base_url=OLLAMA_API_BASE_URL)
wait_for_ollama()
init_db()

index = load_or_create_index()
if index:
    logging.info("openai_compatible: Vector index is ready.")
else:
    logging.error("openai_compatible: Failed to load vector index.")

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def completions():
    if not index:
        return jsonify({"error": "Vector index not available"}), 500

    data = request.get_json()
    messages = data.get("messages", [])
    user_id = data.get("user", "anonymous")
    stream = data.get("stream", False)

    model_id = "elesh-archivist"
    completion_id = str(uuid.uuid4())

    if stream:
        def event_stream():
            try:
                for chunk in stream_archivist_response(messages, index, user_id):
                    try:
                        chunk_json = json.loads(chunk)
                        content = chunk_json.get("response", "")
                        done = chunk_json.get("done", False)

                        if content:
                            yield f"data: {json.dumps({ \
                                'id': completion_id, \
                                'object': 'chat.completion.chunk', \
                                'choices': [{ \
                                    'delta': { 'content': content }, \
                                    'index': 0, \
                                    'finish_reason': None \
                                }], \
                                'model': model_id \
                            })}\n\n"

                        if done:
                            yield f"data: {json.dumps({ \
                                'id': completion_id, \
                                'object': 'chat.completion.chunk', \
                                'choices': [{ \
                                    'delta': {}, \
                                    'index': 0, \
                                    'finish_reason': 'stop' \
                                }], \
                                'model': model_id \
                            })}\n\n"
                            yield "data: [DONE]\n\n"
                            break
                    except Exception:
                        logging.exception("openai_compatible: Failed to parse streamed response chunk")
                        yield "data: [ERROR] Streaming error\n\n"
            except Exception:
                logging.exception("openai_compatible: Streaming failed")
                yield "data: [ERROR] Stream failed\n\n"

        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

    raw_answer = ask_archivist(messages, index, user_id)

    return jsonify({
        "id": completion_id,
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": raw_answer
            },
            "finish_reason": "stop"
        }],
        "model": model_id,
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