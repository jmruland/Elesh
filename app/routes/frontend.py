from flask import Blueprint, render_template, request, jsonify, current_app
from utils.prompt import get_system_prompt, set_system_prompt
from utils.index_utils import load_or_create_index
from utils.logger import logger
import os
from config import LORE_PATH

frontend_bp = Blueprint("frontend", __name__, template_folder="../templates")

def get_file_counts():
    lore_dir = os.path.join(LORE_PATH, "lore")
    rules_dir = os.path.join(LORE_PATH, "rules")
    lore_files = [f for f in os.listdir(lore_dir) if os.path.isfile(os.path.join(lore_dir, f))] if os.path.exists(lore_dir) else []
    rules_files = [f for f in os.listdir(rules_dir) if os.path.isfile(os.path.join(rules_dir, f))] if os.path.exists(rules_dir) else []
    return lore_files, rules_files

@frontend_bp.route("/", methods=["GET"])
def status_page():
    lore_files, rules_files = get_file_counts()
    return render_template(
        "status.html",
        prompt=get_system_prompt(),
        lore_count=len(lore_files),
        rules_count=len(rules_files),
        lore_files=lore_files,
        rules_files=rules_files,
    )

@frontend_bp.route("/renew", methods=["POST"])
def renew():
    index = load_or_create_index()
    current_app.config["INDEX"] = index
    logger.info("Manual frontend reload of index requested.")
    return jsonify({"status": "reloaded"})

@frontend_bp.route("/system_prompt", methods=["POST"])
def update_prompt():
    new_prompt = request.form.get("prompt")
    if new_prompt:
        set_system_prompt(new_prompt)
        index = load_or_create_index()
        current_app.config["INDEX"] = index
        logger.info("System prompt updated and index reloaded via frontend.")
        return jsonify({"status": "saved and reloaded"})
    else:
        logger.warning("No prompt provided to /system_prompt POST.")
        return jsonify({"error": "No prompt provided"}), 400