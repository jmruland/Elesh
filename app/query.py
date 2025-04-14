import os
import requests
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

def get_system_prompt():
    try:
        with open("system.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logging.error("get_system_prompt: Failed to load prompt: %s", e, exc_info=True)
        return ""

def build_prompt(messages, context):
    user_messages = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages if m["role"] != "system"])
    prompt = f"""{get_system_prompt()}

Context:
{context}

{user_messages}

Archivist:"""
    return prompt

def ask_archivist(messages, index):
    try:
        retriever = index.as_retriever()
        context_docs = retriever.retrieve(messages[-1]["content"])
        context_text = "\n\n".join([doc.text for doc in context_docs])

        prompt = build_prompt(messages, context_text)
        logging.debug("ask_archivist: Prompt: %s", prompt[:250])

        response = requests.post(
            os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434") + "/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("response", "[No response generated]")
    except Exception as e:
        logging.error("ask_archivist: Error: %s", e, exc_info=True)
        return "I'm sorry, something went wrong while answering your question."

def stream_archivist_response(messages, index):
    try:
        retriever = index.as_retriever()
        context_docs = retriever.retrieve(messages[-1]["content"])
        context_text = "\n\n".join([doc.text for doc in context_docs])

        prompt = build_prompt(messages, context_text)
        logging.debug("stream_archivist_response: Prompt: %s", prompt[:250])

        response = requests.post(
            os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434") + "/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": True},
            stream=True,
            timeout=60
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                yield line.decode("utf-8")
    except Exception as e:
        logging.error("stream_archivist_response: Error: %s", e, exc_info=True)
        yield '{"response": "[Streaming error]"}'