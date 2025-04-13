from flask import Blueprint, request, Response, stream_with_context, jsonify
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.settings import Settings
from query import ask_archivist, stream_archivist_response, get_system_prompt
import os

openai_bp = Blueprint("openai_compatible", __name__)

# Embedding model setup (nomic-embed-text must be pulled in advance)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# Try to load from vectorstore, otherwise generate from /lore
try:
    from llama_index.core.storage import StorageContext, load_index_from_storage
    storage_context = StorageContext.from_defaults(persist_dir="./vectorstore")
    index = load_index_from_storage(storage_context)
    print("[INFO] Loaded index from persistent vectorstore.")
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
