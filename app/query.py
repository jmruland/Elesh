import os
import requests

def get_system_prompt():
    with open("system.txt", "r") as f:
        return f.read()

def ask_archivist(prompt, index):
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

def stream_archivist_response(prompt, index):
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
