from flask import Flask, request, jsonify
from indexer import load_index
from query import ask_archivist

app = Flask(__name__)
try:
    index = load_index()
except Exception as e:
    print(f"Failed to load index: {e}")
    index = None

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "")
    if index is None:
        return jsonify({"response": "The Archivist is not yet connected to the lore archive. Please try again later."})
    response = ask_archivist(question, index)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
