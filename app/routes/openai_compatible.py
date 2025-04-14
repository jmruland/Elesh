from flask import Blueprint, request, Response, stream_with_context, jsonify
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.settings import Settings
from query import ask_archivist, stream_archivist_response, get_system_prompt
from utils.index_utils import wait_for_ollama, load_or_create_index
from config import VECTORSTORE_DIR, LORE_PATH, MODEL_NAME, OLLAMA_API_BASE_URL
import os, logging, re

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
    """
    Parses the raw answer text into a title and detailed answer.
    Expects the text to contain markers "Title:" and "Answer:".
    If not found, uses a fallback strategy: splits by newline if the first line is short.
    """
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

    if stream:
        def event_stream():
            for chunk in stream_archivist_response(question, index):
                yield f"data: {chunk}\n\n"
        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")
    
    raw_answer = ask_archivist(question, index)
    title, content = parse_answer(raw_answer)
    logging.debug("openai_compatible: Parsed answer - Title: %s, Content: %s", title, content)
    
    response_payload = {
        "id": "chatcmpl-local",
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "title": title,  # Update this field to show the new title.
                "content": content
            },
            "finish_reason": "stop"
        }],
        "model": "elesh-archivist",
        "system_prompt": get_system_prompt()
    }
    return jsonify(response_payload)

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