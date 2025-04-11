# 🧠 Elesh the Archivist

**Elesh** is a fully local, AI-powered in-character NPC designed for use in TTRPGs and fantasy worlds. Elesh serves as the Grand Archivist of your world’s lore — answering player and GM questions strictly using provided documents and worldbuilding files.

Powered by:
- [LlamaIndex](https://github.com/run-llama/llama_index) for Retrieval-Augmented Generation (RAG)
- [Ollama](https://ollama.com) for local LLMs and embeddings
- Flask API for a lightweight interface
- Optional integration with [Open WebUI](https://github.com/open-webui/open-webui)
- **ChatGPT 4o because I'm trash.**
---

## 📦 Docker Hub

Pull the prebuilt image from Docker Hub:

```bash
docker pull jmruland/elesh-archivist:latest
docker run -d \
  --name elesh-archivist \
  -p 5005:5005 \
  -v /mnt/infrastructure/dnd-archivist/lore:/app/lore \
  -v /mnt/infrastructure/dnd-archivist/prompts/system.txt:/app/system.txt \
  -e OLLAMA_API_BASE_URL=http://host.docker.internal:11434 \
  jmruland/elesh-archivist:latest
```

## 📁 Lore Directory Structure
Elesh expects the following layout mounted into the container:

```bash
/mnt/infrastructure/dnd-archivist/
├── lore/              # Markdown or plain text lore files
│   ├── auroran_academy.md
│   ├── solar_order.txt
│   └── map_notes.pdf
├── prompts/
│   └── system.txt     # Elesh's in-character persona description
```

## 🧠 Querying the Archivist
Ask a question with a simple POST:

```bash
curl -X POST http://localhost:5005/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the Solar Order?"}'
Elesh will respond in-character using only indexed lore.
```

## 🔄 How It Works
On container startup:

Loads all .md, .txt, and .pdf lore documents

Builds a searchable embedding index via nomic-embed-text from Ollama

Receives POST requests at /ask

Returns contextual, in-character answers drawn only from the lore

## 🛠 Integration Notes
Use with Open WebUI for a UI

Ollama must have the nomic-embed-text model downloaded:

```bash
ollama pull nomic-embed-text
```
🔁 Continuous Deployment
This repo includes GitHub Actions that:

Build the Docker image on push to main

Push to Docker Hub as jmruland/elesh-archivist:latest

Secrets required:

DOCKERHUB_USERNAME

DOCKERHUB_TOKEN

## ✨ Roadmap
 /refresh endpoint for dynamic lore reloading

 Web UI query panel for players

 Session memory and query logging

 Multi-language or styled NPC responses