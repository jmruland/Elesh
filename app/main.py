from flask import Flask, request, jsonify
from indexer import load_index
from query import ask_archivist

app = Flask(__name__)
index = load_index()

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "")
    response = ask_archivist(question, index)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
