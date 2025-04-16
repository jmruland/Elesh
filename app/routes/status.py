from flask import Blueprint, jsonify, current_app
import os
import json
from utils.logger import logger
from config import LORE_PATH, RULEBOOKS_PATH

status_bp = Blueprint("status", __name__)

@status_bp.route("/status", methods=["GET"])
def status():
    # Report on lore indexes, files, Ollama connection status, etc.
    try:
        lore_lore_path = os.path.join(LORE_PATH, "lore")
        lore_rules_path = os.path.join(LORE_PATH, "rules")
        lore_files = []
        rules_files = []
        if os.path.isdir(lore_lore_path):
            lore_files = [f for f in os.listdir(lore_lore_path) if f.endswith('.md') or f.endswith('.txt')]
        if os.path.isdir(lore_rules_path):
            rules_files = [f for f in os.listdir(lore_rules_path) if f.endswith('.md') or f.endswith('.txt')]

        status_report = {
            "lore_count": len(lore_files),
            "rules_count": len(rules_files),
            "lore_files": lore_files,
            "rules_files": rules_files,
            "lore_path": LORE_PATH,
            "vectorstore_exists": os.path.isdir("./vectorstore"),
        }
        logger.info("Status endpoint called.")
        return jsonify(status_report)
    except Exception as e:
        logger.error("Error in status endpoint: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500