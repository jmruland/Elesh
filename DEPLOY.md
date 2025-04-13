# 🚀 Deployment Instructions for Elesh Archivist

## 📦 Prerequisites
- Docker + Docker Compose
- Optional: GPU support for Ollama

## 🧰 Clone and Configure
```bash
git clone https://github.com/YOURNAME/elesh-archivist.git
cd elesh-archivist
```
- Place your lore files in `./lore`
- Edit `system.txt` to define the archivist’s tone

---

## 🛠️ Start the Stack
```bash
docker compose up --build -d
```

### Confirm Services:
```bash
docker ps
```
You should see:
- `elesh-archivist`
- `ollama`

---

## 🔄 Updating Lore Files
- Add or update files in `./lore`
- Run:
```bash
curl -X POST http://localhost:5005/reload
```
To re-index without restart.

---

## 🌐 Access
- Web UI: `http://localhost:5005/`
- API: `http://localhost:5005/v1/chat/completions`

Ready to plug into your campaign tools!
