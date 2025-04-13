# 📖 Usage Guide for Elesh Archivist

## 🧪 Test Endpoints

```bash
# Health check
curl http://localhost:5005/healthz

# Reload lore index
curl -X POST http://localhost:5005/reload

# Ask a lore question
curl http://localhost:5005/ask -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is the Arcane Commonwealth?"}'

# OpenAI-compatible request
curl http://localhost:5005/v1/chat/completions -X POST -H "Content-Type: application/json" -d '{
  "model": "elesh-archivist",
  "messages": [
    {"role": "user", "content": "Tell me about the Eclipse Covenant."}
  ]
}'
```

---

## 🌐 Web Dashboard

Access your web status UI:
```
http://localhost:5005/
```

It shows:
- Lore directory path
- Total indexed entries
- Ollama connection status (live check)
- Auto-refreshes every 30 seconds

---

## ⚙️ OpenWebUI Integration

1. Go to Settings → Connections
2. Click **Add Connection** → OpenAI Compatible
3. Use:
   - **Name**: `Elesh Archivist`
   - **Base URL**: `http://localhost:5005/v1`
   - **API Key**: anything (ignored)
   - **Model ID**: `elesh-archivist`
4. Save and chat!

---