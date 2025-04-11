FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt .
RUN apt update && apt install -y curl bash iputils-ping \
    && pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

CMD ["python", "main.py"]