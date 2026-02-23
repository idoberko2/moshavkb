#!/bin/bash

# restore_chroma.sh
# Usage: ./restore_chroma.sh <backup_filename>

if [ -z "$1" ]; then
  echo "Usage: ./restore_chroma.sh <backup_filename>"
  echo "Example: ./restore_chroma.sh chroma_backup_20240101.tar.gz"
  exit 1
fi

BACKUP_FILE=$1
COMPOSE_FILE="docker-compose.prod.yml"

# Load version if exists, otherwise default to latest
if [ -f VERSION ]; then
  export IMAGE_TAG=$(cat VERSION)
  echo "Using version: $IMAGE_TAG"
else
  export IMAGE_TAG="latest"
  echo "VERSION file not found, defaulting to latest"
fi

echo "Restoring from backup: $BACKUP_FILE"
echo "Stopping services..."
docker compose -f $COMPOSE_FILE stop

echo "Running restore script..."
# Use --no-deps to avoid starting chroma-db service, preventing file locking
docker compose -f $COMPOSE_FILE run --rm --no-deps mkb-ingest-bot python -m scripts.restore $BACKUP_FILE

echo "Restarting services..."
docker compose -f $COMPOSE_FILE up -d
echo "Restoration complete."
