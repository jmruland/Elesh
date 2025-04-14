import os
import json
import subprocess
from flask import Blueprint, jsonify, render_template
from config import SUMMARY_FILE
from utils.ollama import check_required_ollama_models

status_bp = Blueprint("status", __name__)

def get_docker_space_usage():
    try:
        result = subprocess.run(
            ["docker", "system", "df", "-v"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return "Docker CLI Report:\n\n" + result.stdout
    except Exception:
        return None

def get_filesystem_usage(paths):
    info = []
    for label, path in paths.items():
        try:
            stat = os.statvfs(path)
            total = stat.f_frsize * stat.f_blocks
            free = stat.f_frsize * stat.f_bfree
            used = total - free
            info.append(f"{label} [{path}]: {used / (1024**3):.2f} GB used of {total / (1024**3):.2f} GB")
        except Exception as e:
            info.append(f"{label} [{path}]: ERROR - {e}")
    return "Filesystem Usage:\n\n" + "\n".join(info)

@status_bp.route("/status.json", methods=["GET"])
def status_json():
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "r") as f:
            data = json.load(f)

        missing_models = check_required_ollama_models()
        if missing_models:
            data['ollama_models_missing'] = missing_models

        return jsonify({"status": "ok", "lore": data})

    return jsonify({"status": "unavailable", "message": "No lore summary found."}), 404

@status_bp.route("/status", methods=["GET"])
def status_page():
    lore_path = "Unknown"
    lore_count = 0
    ollama_models_missing = []
    ollama_status = False

    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "r") as f:
            data = json.load(f)
            lore_path = data.get("lore_path", "Unknown")
            lore_count = data.get("total_files", 0)

        missing_models = check_required_ollama_models()
        ollama_models_missing = missing_models
        ollama_status = not bool(missing_models)

    docker_usage = get_docker_space_usage()
    if not docker_usage:
        docker_usage = get_filesystem_usage({
            "Root": "/",
            "Vectorstore": "/vectorstore",
            "Mounts": "/mnt"
        })

    return render_template(
        "status.html",
        lore_path=lore_path,
        lore_count=lore_count,
        ollama_status=ollama_status,
        ollama_models_missing=ollama_models_missing,
        docker_usage=docker_usage
    )