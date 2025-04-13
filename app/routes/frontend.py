from flask import Blueprint, render_template, current_app
import os
import json
import requests
from config import SUMMARY_FILE, LORE_PATH, OLLAMA_API_BASE_URL
from utils.ollama import check_required_ollama_models

frontend_bp = Blueprint("frontend", __name__, template_folder="../templates")

@frontend_bp.route("/")
@frontend_bp.route("/status")
def index():
    lore_data = []
    ollama_status = False
    ollama_models_missing = []

    # Check Ollama live connectivity
    try:
        response = requests.post(
            f"{OLLAMA_API_BASE_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": "test"},
            timeout=3
        )
        if response.status_code == 200:
            ollama_status = True
    except Exception:
        pass

    # Load indexed lore summary if available
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "r") as f:
            lore_data = json.load(f)
        ollama_models_missing = lore_data.get("ollama_models_missing", [])

    return render_template(
        "index.html",
        lore_count=len(lore_data),
        lore_path=LORE_PATH,
        ollama_status=ollama_status,
        ollama_models_missing=ollama_models_missing
    )
