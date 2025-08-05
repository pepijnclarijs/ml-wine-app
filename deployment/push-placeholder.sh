#!/bin/bash

# So that silent errors are avoided
set -euo pipefail

# === Validate user input ===
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <environment>"
  echo "Example: $0 dev"
  exit 1
fi

ENV="$1"

# Validate ENV value
if [[ ! "$ENV" =~ ^(dev|test|acc|prod)$ ]]; then
  echo "Invalid environment: $ENV"
  echo "Must be one of: dev, test, acc, prod"
  exit 1
fi

# === CONFIGURATION ===
DOCKER_USERNAME="pepijnclarijs"
IMAGE_NAME="wine-app"
TAG="${ENV}-latest"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"

# === CHECK REQUIRED FILES ===
if [[ ! -f "Dockerfile" ]]; then
  echo "Dockerfile not found in current directory."
  exit 1
fi

if [[ ! -f "index.html" ]]; then
  echo "index.html not found in current directory."
  exit 1
fi

# === BUILD PLACEHOLDER IMAGE ===
echo "Building placeholder image: ${FULL_IMAGE_NAME}"
docker build -t "${FULL_IMAGE_NAME}" .

# === LOGIN TO DOCKER HUB ===
echo "Logging in to Docker Hub..."
docker login

# === PUSH IMAGE ===
echo "Pushing image to Docker Hub..."
docker push "${FULL_IMAGE_NAME}"

# === DONE ===
echo "Placeholder image pushed: ${FULL_IMAGE_NAME}"
