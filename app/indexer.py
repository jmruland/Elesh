from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, ServiceContext
from llama_index.embeddings.ollama import OllamaEmbedding

def load_index():
    reader = SimpleDirectoryReader(input_dir="./lore", recursive=True)
    docs = reader.load_data()

    embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    service_context = ServiceContext.from_defaults(embed_model=embed_model)

    index = VectorStoreIndex.from_documents(docs, service_context=service_context)
    return index
