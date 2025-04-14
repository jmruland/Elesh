from flask import Blueprint, request, Response, stream_with_context, jsonify
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.settings import Settings
from query import ask_archivist, stream_archivist_response, get_system_prompt
from utils.index_utils import wait_for_ollama, load_or_create_index
from config import VECTORSTORE_DIR, LORE_PATH, MODEL_NAME, OLLAMA_API_BASE_URL
import os, logging, re, json
import uuid

openai_bp = Blueprint("openai_compatible", __name__)
Settings.embed_model = OllamaEmbedding(model_name=MODEL_NAME, base_url=OLLAMA_API_BASE_URL)
wait_for_ollama()
index = load_or_create_index()

def parse_title(text):
    lines = text.splitlines()
    if lines and len(lines[0].split()) <= 12:
        return lines[0].strip()
    return ""

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def completions():
    if index is None:
        return jsonify({"error": "Lore index is not available."}), 500

    data = request.get_json()
    messages = data["messages"]
    stream = data.get("stream", False)
    completion_id = str(uuid.uuid4())
    model_id = "elesh-archivist"

    if stream:
        def event_stream():
            try:
                for chunk in stream_archivist_response(messages, index):
                    try:
                        chunk_json = json.loads(chunk)
                        content = chunk_json.get("response", "")
                        done = chunk_json.get("done", False)

                        if content:
                            yield f"data: {json.dumps({ 'id': completion_id, 'object': 'chat.completion.chunk', 'choices': [{ 'delta': { 'content': content }, 'index': 0, 'finish_reason': None }], 'model': model_id })}\n\n"

                        if done:
                            yield f"data: {json.dumps({ 'id': completion_id, 'object': 'chat.completion.chunk', 'choices': [{ 'delta': {}, 'index': 0, 'finish_reason': 'stop' }], 'model': model_id })}\n\n"
                            yield "data: [DONE]\n\n"
                            break
                    except Exception as e:
                        logging.exception("Failed to parse streamed chunk.")
                        yield "data: [ERROR] Streaming failed.\n\n"
                        break
            except Exception as e:
                logging.exception("Streaming failed")
                yield "data: [ERROR] Internal streaming failure\n\n"

        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

    # Non-streamed response
    raw_answer = ask_archivist(messages, index)
    title = parse_title(raw_answer)

    return jsonify({
        "id": completion_id,
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": raw_answer,
                "title": title
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