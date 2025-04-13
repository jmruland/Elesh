import os
import requests

def get_system_prompt():
    with open("system.txt", "r", encoding="utf-8") as f:
        return f.read()

def ask_archivist(question, index):
    retriever = index.as_retriever()
    context_docs = retriever.retrieve(question)
    context_text = "\n\n".join([doc.text for doc in context_docs])
    system_prompt = get_system_prompt()

    prompt = f"""{system_prompt}

Context:
{context_text}

User: {question}

Archivist:"""

    response = requests.post(
        os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434") + "/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=30
    )

    if response.ok:
        return response.json().get("response", "[No response generated]")
    else:
        return f"[Error] Ollama returned status {response.status_code}: {response.text}"

def stream_archivist_response(question, index):
    retriever = index.as_retriever()
    context_docs = retriever.retrieve(question)
    context_text = "\n\n".join([doc.text for doc in context_docs])
    system_prompt = get_system_prompt()

    prompt = f"""{system_prompt}

Context:
{context_text}

User: {question}

Archivist:"""

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

    for line in response.iter_lines():
        if line:
            yield line.decode("utf-8")
