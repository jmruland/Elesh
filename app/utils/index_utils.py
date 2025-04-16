import os
import time
import requests
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.storage import StorageContext
from utils.logger import logger
from config import (
    OLLAMA_API_BASE_URL,
    MODEL_NAME,
    LORE_PATH,
    RULEBOOKS_PATH,
    VECTORSTORE_DIR,
)

DOCUMENT_TYPES = {
    "lore": LORE_PATH,
    "rules": RULEBOOKS_PATH,
}

def ensure_data_dirs():
    """Ensure all persistent data directories exist."""
    for folder in [LORE_PATH, RULEBOOKS_PATH, VECTORSTORE_DIR]:
        try:
            os.makedirs(folder, exist_ok=True)
            logger.info(f"Ensured directory exists: {folder}")
        except Exception as e:
            logger.error(f"Failed to ensure directory {folder}: {e}")

def wait_for_ollama(url=OLLAMA_API_BASE_URL, timeout=60):
    logger.info("Waiting for Ollama to be ready...")
    start = time.time()
    attempt = 1
    while time.time() - start < timeout:
        logger.info(f"Attempt {attempt}: Checking Ollama at {url}/api/embeddings")
        try:
            r = requests.post(
                f"{url}/api/embeddings",
                json={"model": MODEL_NAME, "prompt": "test"},
                timeout=3
            )
            if r.status_code == 200:
                logger.info("Ollama is ready and embedding model is responsive!")
                return
            else:
                logger.warning(f"Ollama unexpected response code: {r.status_code}, Body: {r.text}")
        except Exception as e:
            logger.warning(f"Waiting... Error: {e}")
        attempt += 1
        time.sleep(2)
    raise RuntimeError("Ollama did not respond to embedding requests in time.")

def get_documents():
    tagged_docs = []
    for doc_type, path in DOCUMENT_TYPES.items():
        if not os.path.isdir(path):
            logger.warning(f"{doc_type.capitalize()} directory {path} does not exist. Skipping.")
            continue
        try:
            reader = SimpleDirectoryReader(input_dir=path, recursive=True)
            docs = reader.load_data()
            for d in docs:
                # Attach type as additional metadata (if possible)
                if hasattr(d, "metadata") and isinstance(d.metadata, dict):
                    d.metadata["type"] = doc_type
            tagged_docs.extend(docs)
            logger.info(f"Loaded {len(docs)} '{doc_type}' documents from {path}.")
        except Exception as e:
            logger.error(f"Error reading documents from {path}: {e}")
    logger.info(f"Total documents loaded: {len(tagged_docs)}")
    if not tagged_docs:
        logger.warning("No files found in any lore or rulebooks directory.")
    return tagged_docs

def build_and_save_index(docs):
    embed_model = OllamaEmbedding(model_name=MODEL_NAME, base_url=OLLAMA_API_BASE_URL)
    Settings.embed_model = embed_model
    logger.info("Creating new vector index from provided documents...")
    index = VectorStoreIndex.from_documents(docs)
    index.storage_context.persist(persist_dir=VECTORSTORE_DIR)
    logger.info(f"Index built and persisted at {VECTORSTORE_DIR}.")
    return index

def load_or_create_index():
    """Ensures directory structure, then loads or builds the vector index."""
    ensure_data_dirs()
    logger.info(f"Attempting to load existing vectorstore from {VECTORSTORE_DIR}...")
    wait_for_ollama()
    try:
        storage_context = StorageContext.from_defaults(persist_dir=VECTORSTORE_DIR)
        index = VectorStoreIndex.load_from_storage(storage_context)
        logger.info("Existing index loaded successfully from disk.")
        return index
    except Exception as e:
        logger.warning(f"No persisted index found or failed to load. ({e})")
        logger.info("Building new index from available documents...")
        docs = get_documents()
        if not docs:
            logger.warning("No documents to index. Returning None index.")
            return None
        return build_and_save_index(docs)