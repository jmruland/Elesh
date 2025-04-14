from flask import Blueprint, request, Response, stream_with_context, jsonify
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.settings import Settings
from query import ask_archivist, stream_archivist_response, get_system_prompt
from utils.index_utils import wait_for_ollama, load_or_create_index
from config import VECTORSTORE_DIR, LORE_PATH, MODEL_NAME, OLLAMA_API_BASE_URL
import uuid
import json
import logging

openai_bp = Blueprint("openai_compatible", __name__)

# Configure the embedding model
Settings.embed_model = OllamaEmbedding(model_name=MODEL_NAME, base_url=OLLAMA_API_BASE_URL)

# Ensure Ollama is online before building index
wait_for_ollama()

# Global shared index
index = load_or_create_index()
if index:
    logging.info("openai_compatible: Lore index loaded.")
else:
    logging.error("openai_compatible: Lore index failed to load.")

def parse_answer(answer_text):
    """
    Parses response into a (title, content) tuple if structured correctly.
    """
    import re
    pattern = r"Title:\s*(.*?)\s*Answer:\s*(.*)"
    match = re.search(pattern, answer_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "", answer_text.strip()

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def completions():
    if index is None:
        return jsonify({"error": "Lore index is not available."}), 500

    data = request.get_json()
    question = data["messages"][-1]["content"]
    stream = data.get("stream", False)
    model_id = "elesh-archivist"
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"

    if stream:
        def event_stream():
            try:
                for chunk in stream_archivist_response(question, index):
                    try:
                        chunk_json = json.loads(chunk)
                        content = chunk_json.get("response", "")
                        done = chunk_json.get("done", False)

                        if content:
                            yield f"data: {json.dumps({\
                                'id': completion_id,\
                                'object': 'chat.completion.chunk',\
                                'choices': [{\
                                    'delta': {'content': content},\
                                    'index': 0,\
                                    'finish_reason': None\
                                }],\
                                'model': model_id\
                            })}\n\n"

                        if done:
                            yield f"data: {json.dumps({\
                                'id': completion_id,\
                                'object': 'chat.completion.chunk',\
                                'choices': [{\
                                    'delta': {},\
                                    'index': 0,\
                                    'finish_reason': 'stop'\
                                }],\
                                'model': model_id\
                            })}\n\n"
                            yield "data: [DONE]\n\n"
                            break
                    except Exception as e:
                        logging.exception("Error parsing streamed response chunk")
                        break
            except Exception as e:
                logging.exception("Streaming response failed")
                yield "data: [ERROR] Streaming failure\n\n"

        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

    # Non-stream fallback
    raw_answer = ask_archivist(question, index)
    _, content = parse_answer(raw_answer)

    return jsonify({
        "id": completion_id,
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content
            },
            "finish_reason": "stop"
        }],
        "model": model_id
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