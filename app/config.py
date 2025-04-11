import os

OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434")
MODEL_NAME = "nomic-embed-text"
LORE_PATH = "./lore"
SUMMARY_FILE = "lore_summary.json"