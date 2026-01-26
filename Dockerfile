FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for fitz/pymupdf sometimes)
# RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables will be passed from docker-compose
# CMD is specified in docker-compose.yml for each service
