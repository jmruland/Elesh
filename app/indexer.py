import time
import requests
import os
from datetime import datetime
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from config import OLLAMA_API_BASE_URL, MODEL_NAME, LORE_PATH, SUMMARY_FILE
from logger import print_doc_preview, write_lore_summary

def wait_for_ollama(url=OLLAMA_API_BASE_URL, timeout=60):
    print("Waiting for Ollama to be ready...")
    start = time.time()
    attempt = 1
    while time.time() - start < timeout:
        print(f"Attempt {attempt}: Checking Ollama at {url}/api/embeddings")
        try:
            r = requests.post(
                f"{url}/api/embeddings",
                json={"model": MODEL_NAME, "prompt": "test"},
                timeout=3
            )
            if r.status_code == 200:
                print(f"[{datetime.now().isoformat()}] Ollama is ready and embedding model is responsive!")
                return
            else:
                print(f"Unexpected response code: {r.status_code}, Body: {r.text}")
        except Exception as e:
            print(f"Waiting... Error: {e}")
        attempt += 1
        time.sleep(2)
    raise RuntimeError("Ollama did not respond to embedding requests in time.")

def load_index():
    print(f"[{datetime.now().isoformat()}] Starting lore index loading...")
    wait_for_ollama()

    reader = SimpleDirectoryReader(input_dir=LORE_PATH, recursive=True)
    docs = reader.load_data()

    print(f"[{datetime.now().isoformat()}] Loaded {len(docs)} document(s).")
    lore_summary = []
    for i, doc in enumerate(docs, start=1):
        preview = print_doc_preview(i, doc)
        lore_summary.append({
            "index": i,
            "timestamp": datetime.now().isoformat(),
            "preview": preview
        })

    write_lore_summary(lore_summary, SUMMARY_FILE)

    embed_model = OllamaEmbedding(model_name=MODEL_NAME, base_url=OLLAMA_API_BASE_URL)
    Settings.embed_model = embed_model

    print(f"[{datetime.now().isoformat()}] Creating vector index...")
    index = VectorStoreIndex.from_documents(docs)
    print(f"[{datetime.now().isoformat()}] Indexing complete.")

    return index