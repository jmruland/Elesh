# app/utils/index_utils.py

import time
import requests
import os
from datetime import datetime
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.storage import StorageContext
from config import OLLAMA_API_BASE_URL, MODEL_NAME, LORE_PATH, SUMMARY_FILE, VECTORSTORE_DIR
from logger import print_doc_preview, write_lore_summary

def wait_for_ollama(timeout=60):
    print("Waiting for Ollama to be ready...")
    start = time.time()
    attempt = 1
    while time.time() - start < timeout:
        try:
            print(f"Attempt {attempt}: Checking Ollama at {OLLAMA_API_BASE_URL}/api/embeddings")
            r = requests.post(
                f"{OLLAMA_API_BASE_URL}/api/embeddings",
                json={"model": MODEL_NAME, "prompt": "test"},
                timeout=3
            )
            if r.status_code == 200:
                print(f"[{datetime.now().isoformat()}] ✅ Ollama is responsive!")
                return
            else:
                print(f"[WARN] Ollama responded with status {r.status_code}")
        except Exception as e:
            print(f"Waiting... Error: {e}")
        attempt += 1
        time.sleep(2)
    raise RuntimeError("Ollama not ready after timeout.")

def build_and_save_index(docs):
    embed_model = OllamaEmbedding(model_name=MODEL_NAME, base_url=OLLAMA_API_BASE_URL)
    Settings.embed_model = embed_model

    print(f"[{datetime.now().isoformat()}] Creating vector index...")
    index = VectorStoreIndex.from_documents(docs)
    index.storage_context.persist(persist_dir=VECTORSTORE_DIR)
    print(f"[{datetime.now().isoformat()}] Indexing complete.")
    return index

def load_or_create_index():
    # Use the new API to load an index from persistent storage.
    wait_for_ollama()

    try:
        storage_context = StorageContext.from_defaults(persist_dir=VECTORSTORE_DIR)
        index = VectorStoreIndex.from_storage(storage_context)
        print("[INFO] Loaded index from persistent vectorstore.")
        return index
    except Exception as e:
        print(f"[WARN] No index found. Building new index... ({e})")

    # Read documents from the lore directory.
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

    # Wrap the document previews into a dictionary so the front-end can call .get() on the JSON.
    summary_payload = {
        "document_previews": lore_summary,
        "ollama_models_missing": []  # Update here if you wish to include actual missing models.
    }
    write_lore_summary(summary_payload, SUMMARY_FILE)

    return build_and_save_index(docs)