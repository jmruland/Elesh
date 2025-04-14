# app/config.py

import os

# Ollama configuration
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "nomic-embed-text")

# Lore configuration
LORE_PATH = os.getenv("LORE_PATH", "./lore")
SUMMARY_FILE = os.getenv("SUMMARY_FILE", "./lore_debug.txt")
VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR", "./vectorstore")

# System prompt for the archivist (persona behavior)
SYSTEM_PROMPT_FILE = os.getenv("SYSTEM_PROMPT_FILE", "./system.txt")