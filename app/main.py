from flask import Flask
from indexer import load_index
from routes.status import status_bp
from routes.ask import ask_bp
from routes.openai_compatible import openai_bp

app = Flask(__name__)

# Register route blueprints
app.register_blueprint(status_bp)
app.register_blueprint(ask_bp)
app.register_blueprint(openai_bp)

# Load vector index once at startup
try:
    app.config["INDEX"] = load_index()
except Exception as e:
    print(f"Failed to load index: {e}")
    app.config["INDEX"] = None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
