import requests
import os

def check_required_ollama_models(models=["llama3", "nomic-embed-text"], base_url=None):
    """
    Checks if the required models are available in the local Ollama instance.

    Args:
        models (list): A list of model names to check.
        base_url (str): Base URL for Ollama, defaults to env var or http://ollama:11434

    Returns:
        list: A list of missing model names, if any.
    """
    base_url = base_url or os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434")
    try:
        res = requests.get(f"{base_url}/api/tags", timeout=5)
        res.raise_for_status()
        tags = res.json().get("models", [])
        available = [tag["name"] for tag in tags]
        missing = [model for model in models if model not in available]
        if missing:
            print(f"[WARN] Missing required models in Ollama: {missing}")
        else:
            print(f"[OK] All required Ollama models are available: {models}")
        return missing
    except Exception as e:
        print(f"[ERROR] Could not verify models from Ollama: {e}")
        return models  # Assume all missing if error
