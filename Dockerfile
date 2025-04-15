FROM python:3.10-slim

# Set working directory to /app (to match the Docker Compose volume mount)
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full application code (assuming app, routes, utils, and templates are in /mnt/infrastructure)
COPY . .

# Ensure runtime directories exist (in case the volume starts empty)
RUN mkdir -p /app/lore/lore /app/lore/rules /app/vectorstore /app/templates

# Default command -- the main.py file must be at /app/main.py in the container!
CMD ["python", "/app/main.py"]