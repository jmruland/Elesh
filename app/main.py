from flask import Flask
import os

from utils.index_utils import load_or_create_index
from utils.logger import logger

# Import all your route blueprints
from routes.ask import ask_bp
from routes.reload import reload_bp
from routes.status import status_bp
from routes.health import health_bp
from routes.openai_compatible import openai_bp
from routes.frontend import frontend_bp   # Make sure the frontend is included

logger.info("Elesh Archivist starting up...")

# Initialize (persistent) index – always loaded on boot and after reloads
try:
    index = load_or_create_index()
    if index is not None:
        logger.info("Vector index is available and loaded.")
    else:
        logger.warning("No documents found for indexing at startup. Archivist will be available but cannot answer lore queries until you add lore/rules files.")
except Exception as e:
    index = None
    logger.error(f"Failed to load vector index: {e}")

# Initialize Flask app
app = Flask(__name__)
app.config["INDEX"] = index

# Register all endpoints/blueprints
app.register_blueprint(ask_bp)
app.register_blueprint(reload_bp)
app.register_blueprint(status_bp)
app.register_blueprint(health_bp)
app.register_blueprint(openai_bp)
app.register_blueprint(frontend_bp)

@app.route("/")
def home():
    return "<h2>Elesh Archivist is up and running! Visit <a href='/'>the status page</a>.</h2>"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5005))
    logger.info(f"Starting app on port {port}")
    app.run(host="0.0.0.0", port=port)