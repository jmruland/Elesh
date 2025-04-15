FROM python:3.10-bullseye

# Set working directory to /app to house your application code
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN apt update && apt install -y curl bash iputils-ping \
    && pip install --no-cache-dir -r requirements.txt \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Copy the full application source (Flask app, routes, utils, templates, etc.)
COPY app/ /app/

# Optionally, ensure required subdirectories for runtime (safe if /data is mounted empty)
RUN mkdir -p /data/lore /data/rulebooks /data/vectorstore /app/templates

# Expose the port Flask will use (optional, for documentation/clarity)
EXPOSE 5005

CMD ["python", "main.py"]