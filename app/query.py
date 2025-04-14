# app/query.py

import os
import requests
import logging
from utils.db import save_message, get_message_history
from config import OLLAMA_API_BASE_URL

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

def get_system_prompt():
    try:
        with open("system.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logging.error("get_system_prompt: %s", e, exc_info=True)
        return ""

def build_prompt_from_messages(messages, context_text):
    system_prompt = next((m["content"] for m in messages if m["role"] == "system"), get_system_prompt())
    prompt = f"{system_prompt.strip()}\n\nContext:\n{context_text.strip()}\n\n"

    for msg in messages:
        if msg["role"] == "user":
            prompt += f"User: {msg['content'].strip()}\n"
        elif msg["role"] == "assistant":
            prompt += f"Archivist: {msg['content'].strip()}\n"

    prompt += "Archivist:"
    return prompt

def ask_archivist(messages, index, user_id="anonymous"):
    try:
        retriever = index.as_retriever()
        latest_question = messages[-1]["content"]
        context_docs = retriever.retrieve(latest_question)
        context_text = "\n\n".join([doc.text for doc in context_docs])
        full_messages = get_message_history(user_id) + messages

        prompt = build_prompt_from_messages(full_messages, context_text)
        save_message(user_id, "user", latest_question)

        response = requests.post(
            f"{OLLAMA_API_BASE_URL}/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=60
        )

        if response.ok:
            output = response.json().get("response", "")
            save_message(user_id, "assistant", output)
            return output
        else:
            return f"[Error] Ollama returned {response.status_code}"
    except Exception as e:
        logging.exception("ask_archivist error")
        return "I'm sorry, something went wrong."

def stream_archivist_response(messages, index, user_id="anonymous"):
    try:
        retriever = index.as_retriever()
        latest_question = messages[-1]["content"]
        context_docs = retriever.retrieve(latest_question)
        context_text = "\n\n".join([doc.text for doc in context_docs])
        full_messages = get_message_history(user_id) + messages

        prompt = build_prompt_from_messages(full_messages, context_text)
        save_message(user_id, "user", latest_question)

        response = requests.post(
            f"{OLLAMA_API_BASE_URL}/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": True},
            stream=True,
            timeout=120
        )

        for line in response.iter_lines():
            if line:
                yield line.decode("utf-8")
    except Exception as e:
        logging.exception("stream_archivist_response error")
        yield '{"error": "streaming failed."}'