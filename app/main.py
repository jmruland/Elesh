from flask import Flask
import os

from routes.status import status_bp
from routes.ask import ask_bp
from routes.openai_compatible import openai_bp
from routes.health import health_bp
from routes.reload import reload_bp
from routes.frontend import frontend_bp

from utils.index_utils import load_or_create_index
from utils.ollama import check_required_ollama_models

# Verify embedding model is available
check_required_ollama_models()

# Load the persistent or generated index
index = load_or_create_index()

# Init Flask app
app = Flask(__name__)
app.config["INDEX"] = index

# Register all routes
app.register_blueprint(status_bp)
app.register_blueprint(ask_bp)
app.register_blueprint(openai_bp)
app.register_blueprint(health_bp)
app.register_blueprint(reload_bp)
app.register_blueprint(frontend_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)