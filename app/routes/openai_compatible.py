from flask import Blueprint, request, Response, stream_with_context, jsonify
from collections import defaultdict, deque
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import load_index_from_storage
from query import ask_archivist, stream_archivist_response, get_system_prompt

openai_bp = Blueprint("openai_compatible", __name__)

# Load vector index once
storage_context = StorageContext.from_defaults(persist_dir="./vectorstore")
index = load_index_from_storage(storage_context)

# Store recent messages per user (by IP address)
user_sessions = defaultdict(lambda: deque(maxlen=10))

@openai_bp.route("/v1/chat/completions", methods=["POST"])
def completions():
    data = request.get_json()
    stream = data.get("stream", False)
    messages = data["messages"]

    # Identify the user
    user_id = request.remote_addr or "anonymous"
    user_sessions[user_id].extend(messages)

    print(f"[USER] {user_id} sent {len(messages)} message(s)")

    # Reconstruct full conversation as prompt
    conversation = "\n".join(
        f"{m['role'].capitalize()}: {m['content']}" for m in user_sessions[user_id]
    )
    prompt = f"{get_system_prompt()}\n\n{conversation}\n\nArchivist:"
    print(f"[PROMPT] {prompt[:300]}...")

    if stream:
        def event_stream():
            for chunk in stream_archivist_response(prompt, index):
                print(f"[STREAM] {chunk}")
                yield f"data: {chunk}\n\n"
        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

    answer = ask_archivist(prompt, index)
    print(f"[RESPONSE] {answer}")

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
