from flask import Blueprint, jsonify
import os
import json
from config import SUMMARY_FILE
from utils.ollama import check_required_ollama_models  # ✅ Added import

status_bp = Blueprint("status", __name__)

@status_bp.route("/status", methods=["GET"])
def status():
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "r") as f:
            data = json.load(f)

        # ✅ Check if required models are missing from Ollama
        missing_models = check_required_ollama_models()
        if missing_models:
            data['ollama_models_missing'] = missing_models

        return jsonify({"status": "ok", "lore": data})

    return jsonify({"status": "unavailable", "message": "No lore summary found."}), 404
