from flask import Blueprint, jsonify, current_app
from indexer import load_index

reload_bp = Blueprint("reload", __name__)

@reload_bp.route("/reload", methods=["POST"])
def reload():
    try:
        current_app.config["INDEX"] = load_index()
        return jsonify({"status": "reloaded"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500