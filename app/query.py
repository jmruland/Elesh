import openai
import os

def get_system_prompt():
    with open("system.txt", "r") as f:
        return f.read()

def ask_archivist(question, index):
    retriever = index.as_retriever()
    context_docs = retriever.retrieve(question)
    context_text = "\n\n".join([doc.text for doc in context_docs])

    system_prompt = get_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{context_text}\n\n{question}"}
    ]

    openai.api_base = os.getenv("OLLAMA_API_BASE_URL", "http://ollama:11434")
    openai.api_key = "ollama"  # placeholder

    response = openai.ChatCompletion.create(
        model="llama3",
        messages=messages,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']