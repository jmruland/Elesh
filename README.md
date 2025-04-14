# Elesh Archivist

A self-hosted AI-powered NPC designed to act as your D&D world's archivist. Elesh answers campaign lore questions using your own notes, formatted documents, or adventure texts. Built to integrate cleanly with OpenWebUI and Ollama.

---

## 🧠 Features

- 🧾 **Lore indexing** from Markdown and plaintext documents
- 🗣️ **In-character responses** from Elesh, the snarky Grand Archivist
- 📁 **Custom system prompt** defined in `system.txt`
- ⚡ **Ollama embedding + model support**
- 🔄 **Auto-indexing and reload endpoint**
- 🌐 **Web status frontend**
- 🧪 **OpenAI-compatible API for tools like OpenWebUI**

---

## 📦 Architecture Overview

- **Flask** backend with modular route blueprints
- **LlamaIndex** for semantic search and vector storage
- **Nomic-embed-text** via Ollama for fast local embedding
- **Markdown + plaintext** ingestion from `./lore`
- **Streaming response support** via SSE (event streams)
- **Persistent vectorstore** under `./vectorstore/`

---

## 🔗 Documentation

- [Deployment Guide](./DEPLOY.md)
- [Usage + API Reference](./USAGE.md)
- `system.txt` for prompt persona config
- `lore_debug.txt` for indexing previews