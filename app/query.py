import os
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_system_prompt():
    try:
        with open("system.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        logging.debug("get_system_prompt: System prompt loaded successfully.")
        return prompt
    except Exception as e:
        logging.error("get_system_prompt: Error loading system prompt: %s", e, exc_info=True)
        return ""

def build_prompt_from_messages(messages, context_text):
    """Builds a prompt string from OpenAI-compatible messages."""
    system_prompt = next(
        (msg["content"] for msg in messages if msg["role"] == "system"),
        get_system_prompt()
    )

    prompt = f"{system_prompt.strip()}\n\nContext:\n{context_text.strip()}\n\n"

    for msg in messages:
        if msg["role"] == "user":
            prompt += f"User: {msg['content'].strip()}\n"
        elif msg["role"] == "assistant":
            prompt += f"Archivist: {msg['content'].strip()}\n"

    # Final instruction (reinforced format)
    prompt += (
        "Archivist (please provide your answer in exactly two parts, each on a separate line. "
        "The first line must begin with 'Title:' followed by a concise title with an emoji. "
        "The second line must begin with 'Answer:' followed by a detailed, narrative answer addressing the question fully. "
        "Do not include any other text):"
    )

    logging.debug("build_prompt_from_messages: Constructed prompt (first 300 chars):\n%s", prompt[:300])
    return prompt

def ask_archivist(messages, index):
    try:
        retriever = index.as_retriever()
        latest_question = messages[-1]["content"]
        context_docs = retriever.retrieve(latest_question)
        logging.debug("ask_archivist: Retrieved %d context documents.", len(context_docs))

        context_text = "\n\n".join([doc.text for doc in context_docs])
        prompt = build_prompt_from_messages(messages, context_text)

        response = requests.post(
            os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434") + "/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.ok:
            json_resp = response.json()
            return json_resp.get("response", "[No response generated]")
        else:
            logging.error("ask_archivist: Ollama error %s: %s", response.status_code, response.text)
            return f"[Error] Ollama returned status {response.status_code}"
    except Exception as e:
        logging.exception("ask_archivist: Exception occurred")
        return "I'm sorry, something went wrong while answering your question."

def stream_archivist_response(messages, index):
    try:
        retriever = index.as_retriever()
        latest_question = messages[-1]["content"]
        context_docs = retriever.retrieve(latest_question)
        logging.debug("stream_archivist_response: Retrieved %d context documents.", len(context_docs))

        context_text = "\n\n".join([doc.text for doc in context_docs])
        prompt = build_prompt_from_messages(messages, context_text)

        response = requests.post(
            os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434") + "/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": True
            },
            stream=True,
            timeout=120
        )

        for line in response.iter_lines():
            if line:
                yield line.decode("utf-8")
    except Exception as e:
        logging.exception("stream_archivist_response: Streaming failure")
        yield '{"error": "Streaming failed."}'