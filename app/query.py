import logging
from utils.logger import logger

def ask_archivist(messages, index, user_id="anonymous", corpus="both"):
    """
    Query the archivist with optional filtering between lore and rulebook documents.
    :param messages: List of chat messages.
    :param index: VectorStoreIndex instance.
    :param user_id: (optional) User for message history, future extension.
    :param corpus: "lore", "rules", or "both"
    :return: String response from the archivist.
    """
    try:
        query = messages[-1]["content"]
        logger.info(f"[{user_id}] Query: {query} | Corpus: {corpus}")

        retriever = index.as_retriever()
        docs = retriever.retrieve(query)
        # Filter docs by corpus if requested
        if corpus in ("lore", "rules"):
            filtered = [d for d in docs if getattr(d, "extra_metadata", {}).get("type") == corpus]
            logger.info(f"Filtered {len(filtered)}/{len(docs)} docs for corpus '{corpus}'.")
            docs = filtered

        context_text = "\n\n".join([d.text for d in docs])
        prompt = build_prompt_from_messages(messages, context_text)
        # Optionally save_message(user_id, "user", query) -- extend for true chat history

        # --- Replace with call to your LLM/ollama logic, e.g.:
        import requests
        from config import OLLAMA_API_BASE_URL
        response = requests.post(
            f"{OLLAMA_API_BASE_URL}/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=60
        )
        if response.ok:
            output = response.json().get("response", "")
            logger.info(f"[{user_id}] Archivist Response: {output[:75]}...")
            return output
        else:
            logger.error(f"Ollama error {response.status_code}: {response.text}")
            return f"[Error] Ollama returned {response.status_code}"
    except Exception as e:
        logger.exception("ask_archivist error")
        return "I'm sorry, something went wrong."

def build_prompt_from_messages(messages, context_text):
    # Use your return from get_system_prompt() or .system.txt logic here as before.
    from config import SYSTEM_PROMPT_FILE
    def get_system_prompt():
        try:
            with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error("get_system_prompt: %s", e, exc_info=True)
            return ""
    system_prompt = next((m["content"] for m in messages if m["role"] == "system"), get_system_prompt())
    prompt = f"{system_prompt.strip()}\n\nContext:\n{context_text.strip()}\n\n"
    for msg in messages:
        if msg["role"] == "user":
            prompt += f"User: {msg['content'].strip()}\n"
        elif msg["role"] == "assistant":
            prompt += f"Archivist: {msg['content'].strip()}\n"
    prompt += "Archivist:"
    return prompt