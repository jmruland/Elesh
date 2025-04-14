import os
import requests
import logging

# Configure logging if it hasn't already been configured.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_system_prompt():
    try:
        with open("system.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        logging.debug("get_system_prompt: Loaded system prompt successfully.")
        return prompt
    except Exception as e:
        logging.error("get_system_prompt: Could not load system prompt: %s", e, exc_info=True)
        return ""

def ask_archivist(question, index):
    logging.debug("ask_archivist: Received question: %s", question)
    try:
        # Retrieve relevant context from the index.
        retriever = index.as_retriever()
        context_docs = retriever.retrieve(question)
        logging.debug("ask_archivist: Retrieved %d context documents.", len(context_docs))
        context_text = "\n\n".join([doc.text for doc in context_docs])
        system_prompt = get_system_prompt()

        # Modified prompt: instruct the model to provide a complete narrative answer.
        prompt = f"""{system_prompt}

Context:
{context_text}

User: {question}

Archivist (please provide a detailed, comprehensive answer in plain text that addresses the user's question fully):"""
        
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
        logging.debug("ask_archivist: Received response status: %s", response.status_code)

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

        # Modified prompt for streaming version as well.
        prompt = f"""{system_prompt}

Context:
{context_text}

User: {question}

Archivist (please provide a detailed, comprehensive answer in plain text that fully addresses the user's query):"""
        
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
        logging.debug("stream_archivist_response: Received response status: %s", response.status_code)
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                logging.debug("stream_archivist_response: Yielding line: %s", decoded_line)
                yield decoded_line
    except Exception as e:
        logging.error("stream_archivist_response: Exception while streaming response: %s", e, exc_info=True)
        yield "I'm sorry, something went wrong during streaming the response."