import os
import requests
import logging

# Configure logging if not already configured.
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

def ask_archivist(question, index):
    logging.debug("ask_archivist: Received question: %s", question)
    try:
        retriever = index.as_retriever()
        context_docs = retriever.retrieve(question)
        logging.debug("ask_archivist: Retrieved %d context documents.", len(context_docs))
        context_text = "\n\n".join([doc.text for doc in context_docs])
        system_prompt = get_system_prompt()
        
        # Updated prompt: Instruct the model to output exactly two parts.
        prompt = f"""{system_prompt}

Context:
{context_text}

User: {question}

Archivist (please provide your answer in exactly two parts, each on a separate line. The first line must begin with "Title:" followed by a concise title with an emoji. The second line must begin with "Answer:" followed by a detailed, narrative answer addressing the question fully. Do not include any other text):
"""
        logging.debug("ask_archivist: Constructed prompt (first 200 chars): %s", prompt[:200])
        
        response = requests.post(
            os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434") + "/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        logging.debug("ask_archivist: Response status: %s", response.status_code)
        
        if response.ok:
            json_resp = response.json()
            logging.debug("ask_archivist: Response JSON: %s", json_resp)
            return json_resp.get("response", "[No response generated]")
        else:
            error_message = f"[Error] Ollama returned status {response.status_code}: {response.text}"
            logging.error("ask_archivist: %s", error_message)
            return error_message
    except Exception as e:
        logging.error("ask_archivist: Exception while processing question: %s", e, exc_info=True)
        return "I'm sorry, something went wrong while answering your question."

def stream_archivist_response(question, index):
    logging.debug("stream_archivist_response: Received question: %s", question)
    try:
        retriever = index.as_retriever()
        context_docs = retriever.retrieve(question)
        logging.debug("stream_archivist_response: Retrieved %d context documents.", len(context_docs))
        context_text = "\n\n".join([doc.text for doc in context_docs])
        system_prompt = get_system_prompt()
        
        prompt = f"""{system_prompt}

Context:
{context_text}

User: {question}

Archivist (please provide your answer in exactly two parts, each on a separate line. The first line must start with "Title:" followed by a concise title with an emoji. The second line must start with "Answer:" followed by a detailed explanation of your answer. Do not include any extra text):
"""
        logging.debug("stream_archivist_response: Constructed prompt (first 200 chars): %s", prompt[:200])
        
        response = requests.post(
            os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434") + "/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": True
            },
            stream=True,
            timeout=60
        )
        logging.debug("stream_archivist_response: Response status: %s", response.status_code)
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                logging.debug("stream_archivist_response: Yielding line: %s", decoded_line)
                yield decoded_line
    except Exception as e:
        logging.error("stream_archivist_response: Exception while streaming response: %s", e, exc_info=True)
        yield "I'm sorry, something went wrong during streaming the response."