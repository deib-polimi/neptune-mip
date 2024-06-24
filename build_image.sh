#!/bin/bash

# Variables
IMAGE="neptune-mip"
TAG="latest"
PORT="5000"

# Stop all running containers from the specified image
echo "Stopping all running containers from image ${IMAGE}:${TAG}..."
docker ps --filter "ancestor=${IMAGE}:${TAG}" --format "{{.ID}}" | xargs -r docker stop

# Build the Docker image
echo "Building the Docker image ${IMAGE}:${TAG}..."
docker build -t ${IMAGE}:${TAG} .

# Run a new container from the newly built image
echo "Running the Docker container from image ${IMAGE}:${TAG}..."
docker run -it -p ${PORT}:${PORT} ${IMAGE}:${TAG}
