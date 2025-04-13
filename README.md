# Elesh Archivist

An OpenAI-compatible, self-hosted D&D lore assistant powered by Flask and LlamaIndex, built to serve as an in-character NPC Archivist that can answer questions about your world.

---

## 🚀 Features
- Loads campaign lore from markdown or text files
- Generates vector index using LlamaIndex and Ollama embeddings
- Exposes a `/v1/chat/completions` endpoint compatible with OpenWebUI
- Supports streaming responses (`stream: true`)
- Includes `/ask`, `/reload`, `/status`, and `/healthz` endpoints

---

## 📁 Folder Layout
- `app/`: Flask app and logic
- `tests/`: Pytest-based unit and integration tests
- `Dockerfile`: containerization setup
- `docker-compose.yml`: deployment stack

---

## 🧪 Test Endpoints

```bash
# Health check
curl http://localhost:5005/healthz

# Reload lore
curl -X POST http://localhost:5005/reload

# Ask a question
curl http://localhost:5005/ask \
  -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is the Arcane Commonwealth?"}'

# OpenAI-compatible request
curl http://localhost:5005/v1/chat/completions \
  -X POST -H "Content-Type: application/json" \
  -d '{
    "model": "elesh-archivist",
    "messages": [
      {"role": "user", "content": "Tell me about Arden."}
    ]
  }'
```

---

## 📦 Usage with OpenWebUI
1. Go to Settings → Connections
2. Click **Add Connection** → Select `OpenAI Compatible`
3. Fill in:
   - **Name**: `Elesh Archivist`
   - **Base URL**: `http://localhost:5005/v1`
   - **API Key**: `ollama`
   - **Model ID(s)**: `elesh-archivist`
4. Save and test inside OpenWebUI!

---

## 📄 License
MIT
