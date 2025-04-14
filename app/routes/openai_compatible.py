from flask import Blueprint, request, Response, stream_with_context, jsonify
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from query import ask_archivist, stream_archivist_response, get_system_prompt
from utils.index_utils import wait_for_ollama
import os

openai_bp = Blueprint("openai_compatible", __name__)

# === Ensure Ollama is ready ===
wait_for_ollama()

# === Embedding model setup ===
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

VECTORSTORE_DIR = "./vectorstore"

# === Load index from disk or recreate ===
try:
    index = load_index_from_storage(persist_dir=VECTORSTORE_DIR)
    print(f"[INFO] Loaded index from {VECTORSTORE_DIR}")
except Exception as e:
    print(f"[WARN] No index found. Creating temporary blank index from ./lore... ({e})")
    docs = SimpleDirectoryReader("./lore").load_data()
    index = VectorStoreIndex.from_documents(docs)

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def completions():
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
