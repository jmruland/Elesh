import time
import requests
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.ollama import OllamaEmbedding

def wait_for_ollama(url="http://ollama:11434", timeout=60):
    print("Waiting for Ollama to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print("Ollama is up!")
                return
        except Exception as e:
            print(f"Waiting... ({e})")
        time.sleep(5)
    raise RuntimeError("Ollama did not become available in time.")

def load_index():
    wait_for_ollama()

    reader = SimpleDirectoryReader(input_dir="./lore", recursive=True)
    docs = reader.load_data()

    embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.embed_model = embed_model

    index = VectorStoreIndex.from_documents(docs)
    return index