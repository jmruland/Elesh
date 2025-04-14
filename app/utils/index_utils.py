# app/utils/index_utils.py

import time
import requests
import os
from datetime import datetime
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from config import OLLAMA_API_BASE_URL, MODEL_NAME, LORE_PATH, SUMMARY_FILE, VECTORSTORE_DIR
from logger import print_doc_preview, write_lore_summary

def wait_for_ollama(timeout=60):
    print("Waiting for Ollama to be ready...")
    start = time.time()
    attempt = 1
    while time.time() - start < timeout:
        print(f"Attempt {attempt}: Checking Ollama at {OLLAMA_API_BASE_URL}/api/embeddings")
        try:
            r = requests.post(
                f"{OLLAMA_API_BASE_URL}/api/embeddings",
                json={"model": MODEL_NAME, "prompt": "test"},
                timeout=3
            )
            if r.status_code == 200:
                print(f"[{datetime.now().isoformat()}] ✅ Ollama is responsive!")
                return
            else:
                print(f"⚠️ Unexpected status: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"❌ Waiting... Error: {e}")
        time.sleep(2)
        attempt += 1
    raise RuntimeError("Ollama not ready after timeout.")

def load_documents():
    print(f"[{datetime.now().isoformat()}] Loading documents from: {LORE_PATH}")
    reader = SimpleDirectoryReader(input_dir=LORE_PATH, recursive=True)
    return reader.load_data()

def summarize_lore(docs):
    print(f"[{datetime.now().isoformat()}] Creating lore summary...")
    summary = []
    for i, doc in enumerate(docs, start=1):
        preview = print_doc_preview(i, doc)
        summary.append({
            "index": i,
            "timestamp": datetime.now().isoformat(),
            "preview": preview
        })
    write_lore_summary(summary, SUMMARY_FILE)
    return summary

def build_and_save_index(docs):
    print(f"[{datetime.now().isoformat()}] Building index...")
    index
