from flask import Blueprint, render_template, current_app
import os

frontend_bp = Blueprint("frontend", __name__, template_folder="../templates")

@frontend_bp.route("/")
@frontend_bp.route("/status")
def index():
    # Access configuration and status
    lore_path = current_app.config.get("LORE_PATH", "./lore")
    vectorstore_path = current_app.config.get("VECTORSTORE_DIR", "./vectorstore")
    # Count lore and rulebook entries
    lore_dir = os.path.join(lore_path, "lore")
    rules_dir = os.path.join(lore_path, "rules")
    lore_files = []
    rules_files = []
    if os.path.isdir(lore_dir):
        lore_files = [f for f in os.listdir(lore_dir) if f.endswith('.md') or f.endswith('.txt')]
    if os.path.isdir(rules_dir):
        rules_files = [f for f in os.listdir(rules_dir) if f.endswith('.md') or f.endswith('.txt')]
    vectorstore_exists = os.path.isdir(vectorstore_path)

    return render_template(
        "status.html",
        lore_count=len(lore_files),
        rules_count=len(rules_files),
        lore_files=lore_files,
        rules_files=rules_files,
        lore_path=lore_path,
        vectorstore_exists=vectorstore_exists,
    )