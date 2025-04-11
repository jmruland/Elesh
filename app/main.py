from flask import Flask
from routes.status import status_bp
from routes.ask import ask_bp
from indexer import load_index

app = Flask(__name__)
app.register_blueprint(status_bp)
app.register_blueprint(ask_bp)

try:
    app.config["INDEX"] = load_index()
except Exception as e:
    print(f"Failed to load index: {e}")
    app.config["INDEX"] = None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)