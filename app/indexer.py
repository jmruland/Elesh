from llama_index import SimpleDirectoryReader, VectorStoreIndex

def load_index():
    reader = SimpleDirectoryReader(input_dir="./lore", recursive=True)
    docs = reader.load_data()
    index = VectorStoreIndex.from_documents(docs)
    return index