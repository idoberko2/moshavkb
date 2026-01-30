#!/bin/bash

# backup_chroma.sh
# Usage: ./backup_chroma.sh

COMPOSE_FILE="docker-compose.prod.yml"

# Load version if exists, otherwise default to latest
if [ -f VERSION ]; then
  export IMAGE_TAG=$(cat VERSION)
  echo "Using version: $IMAGE_TAG"
else
  export IMAGE_TAG="latest"
  echo "VERSION file not found, defaulting to latest"
fi

echo "Starting ChromaDB Backup..."
docker compose -f $COMPOSE_FILE run --rm mkb-ingest-bot python -m scripts.backup
echo "Backup command finished."
