import os
import requests

def get_system_prompt():
    with open("system.txt", "r") as f:
        return f.read()

def ask_archivist(question, index):
    retriever = index.as_retriever()
    context_docs = retriever.retrieve(question)
    context_text = "\n\n".join([doc.text for doc in context_docs])

    system_prompt = get_system_prompt()

    prompt = f"{system_prompt}\n\nContext:\n{context_text}\n\nUser: {question}\n\nArchivist:"

    response = requests.post(
        os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434") + "/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=30
    )

    return response.json().get("response", "[No response generated]")
