#!/bin/bash

# deploy.sh
# Usage: ./deploy.sh <version_tag>
# Example: ./deploy.sh 1.0.1

if [ -z "$1" ]; then
  echo "Usage: ./deploy.sh <version_tag>"
  exit 1
fi

VERSION=$1
COMPOSE_FILE="docker-compose.prod.yml"

echo "Deploying version: $VERSION"

# Export the version so docker-compose can use it
export IMAGE_TAG=$VERSION

# Save version to file for other scripts
echo "$VERSION" > VERSION

docker compose -f $COMPOSE_FILE down
docker compose -f $COMPOSE_FILE pull
docker compose -f $COMPOSE_FILE up -d

echo "Deployment of $VERSION complete."
