from flask import Flask
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

from routes.status import status_bp
from routes.ask import ask_bp
from routes.openai_compatible import openai_bp
from routes.health import health_bp
from routes.reload import reload_bp
from query import get_system_prompt

app = Flask(__name__)

# Global index variable
index = None

def init_index():
    global index
    vectorstore_path = "./vectorstore"

    if os.path.exists(os.path.join(vectorstore_path, "docstore.json")):
        print("[INFO] Loading existing vector index...")
        storage_context = StorageContext.from_defaults(persist_dir=vectorstore_path)
        index = load_index_from_storage(storage_context)
    else:
        print("[WARN] No vector index found. Indexing documents from /lore...")
        docs = SimpleDirectoryReader("./lore").load_data()
        index = VectorStoreIndex.from_documents(docs)
        index.storage_context.persist()
        print("[INFO] Indexing complete and saved to disk.")

# Initialize the index once Flask is running
@app.before_first_request
def setup_index():
    init_index()

# Register blueprints
app.register_blueprint(status_bp)
app.register_blueprint(ask_bp)
app.register_blueprint(openai_bp)
app.register_blueprint(health_bp)
app.register_blueprint(reload_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
