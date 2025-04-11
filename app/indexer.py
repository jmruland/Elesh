import time
import requests
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.ollama import OllamaEmbedding

def wait_for_ollama(url="http://ollama:11434", timeout=60):
    print("Waiting for Ollama to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.post(
                f"{url}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": "test"}
            )
            if r.status_code == 200:
                print("Ollama is ready and embedding model is responsive!")
                return
        except Exception as e:
            print(f"Waiting... ({e})")
        time.sleep(5)
    raise RuntimeError("Ollama did not respond to embedding requests in time.")

def load_index():
    wait_for_ollama()

    reader = SimpleDirectoryReader(input_dir="./lore", recursive=True)
    docs = reader.load_data()

    embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.embed_model = embed_model

    index = VectorStoreIndex.from_documents(docs)
    return index