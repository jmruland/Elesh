FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Ensure runtime directories
RUN mkdir -p /app/lore /app/vectorstore /app/templates /app/static

COPY . .

CMD ["python", "app/main.py"]
