from flask import Blueprint, request, jsonify, current_app
from query import ask_archivist

ask_bp = Blueprint("ask", __name__)

@ask_bp.route("/ask", methods=["POST"])
def ask():
    index = current_app.config.get("INDEX")
    data = request.get_json()
    question = data.get("question", "")

    if not index:
        return jsonify({"response": "The Archivist is not yet connected to the lore archive."})

    response = ask_archivist(question, index)
    return jsonify({"response": response})