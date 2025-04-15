import os
from datetime import datetime
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.storage import StorageContext
from utils.logger import logger
from config import OLLAMA_API_BASE_URL, MODEL_NAME, LORE_PATH, VECTORSTORE_DIR

DOCUMENT_TYPES = {
    "lore": os.path.join(LORE_PATH, "lore"),
    "rules": os.path.join(LORE_PATH, "rules"),
}

def ensure_lore_dirs():
    """Ensure that relevant directories exist for lore and rules."""
    for folder in [LORE_PATH] + list(DOCUMENT_TYPES.values()):
        try:
            os.makedirs(folder, exist_ok=True)
            logger.info(f"Ensured directory exists: {folder}")
        except Exception as e:
            logger.error(f"Failed to ensure directory {folder}: {e}")

def get_documents():
    tagged_docs = []
    for doc_type, path in DOCUMENT_TYPES.items():
        if not os.path.isdir(path):
            logger.warning(f"{doc_type.capitalize()} directory {path} does not exist. Skipping.")
            continue
        reader = SimpleDirectoryReader(input_dir=path, recursive=True)
        try:
            docs = reader.load_data()
        except Exception as e:
            logger.error(f"Error loading documents from {path}: {e}")
            continue
        for d in docs:
            d.extra_metadata = {"type": doc_type}
        tagged_docs.extend(docs)
        logger.info(f"Loaded {len(docs)} '{doc_type}' documents from {path}.")
    logger.info(f"Total documents loaded: {len(tagged_docs)}")
    if not tagged_docs:
        logger.error("No files found in any lore or rules directory. Indexing aborted.")
        raise RuntimeError("No files found in lore or rules.")
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
    ensure_lore_dirs()
    logger.info(f"Attempting to load existing vectorstore from {VECTORSTORE_DIR}...")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=VECTORSTORE_DIR)
        index = VectorStoreIndex.load_from_storage(storage_context)
        logger.info("Existing index loaded successfully from disk.")
        return index
    except Exception as e:
        logger.warning(f"No persisted index found or failed to load. ({e})")
        logger.info("Building new index from available documents...")
        try:
            docs = get_documents()
            return build_and_save_index(docs)
        except Exception as final_e:
            logger.error(f"Failed to load vector index: {final_e}")
            raise