from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/healthz", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
