FROM python:3.10-slim

# Set working directory to /app to house your application code
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full application source (Flask app, routes, utils, templates, etc.)
COPY . .

# Optionally, ensure required subdirectories for runtime (safe if /data is mounted empty)
RUN mkdir -p /data/lore /data/rulebooks /data/vectorstore /app/templates

# Expose the port Flask will use (optional, for documentation/clarity)
EXPOSE 5005

# NOTE: At runtime, mount /mnt/infrastructure (host) to /data (container)
# All persistent data, books, vectorstore, and prompt will live there.

# Start the Flask app, expecting main.py to be in /app
CMD ["python", "/app/main.py"]