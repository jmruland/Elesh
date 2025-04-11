from flask import Blueprint, jsonify
import os
import json
from config import SUMMARY_FILE

status_bp = Blueprint("status", __name__)

@status_bp.route("/status", methods=["GET"])
def status():
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "r") as f:
            data = json.load(f)
        return jsonify({"status": "ok", "lore": data})
    return jsonify({"status": "unavailable", "message": "No lore summary found."}), 404