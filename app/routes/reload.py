from flask import Blueprint, jsonify, current_app
from indexer import load_index
import os
import json

reload_bp = Blueprint("reload", __name__)

@reload_bp.route("/reload", methods=["POST"])
def reload():
    try:
        index = load_index()
        current_app.config["INDEX"] = index

        summary = {}
        if os.path.exists("lore_summary.json"):
            with open("lore_summary.json", "r") as f:
                data = json.load(f)
                summary = {
                    "count": len(data),
                    "latest": data[-1] if data else {}
                }

        return jsonify({
            "status": "reloaded",
            "documents": summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500