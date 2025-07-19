#!/bin/bash

echo "Building Docker image..."
docker build -f Dockerfile -t breitbandmessung .

echo "Setting permissions..."
chmod +x $PWD/*.sh

echo "Stopping and removing existing container..."
docker stop breitbandmessung >> /dev/null 2>&1
docker rm breitbandmessung >> /dev/null 2>&1

echo "Creating directories..."
mkdir -p $PWD/config
mkdir -p $PWD/messprotokolle

echo "Copying default config with INI format..."
cp config.cfg.defaults config/config.cfg
echo "Config file created with [General] section header"

echo "Current directory: $PWD"
echo "Config directory: $PWD/config"
echo "Messprotokolle directory: $PWD/messprotokolle"

echo "Creating Docker container with volume mappings..."
docker create \
  -v $PWD/config/:/usr/src/app/config:rw \
  -v $PWD/messprotokolle:/export:rw \
  --name "breitbandmessung" \
  breitbandmessung:latest

echo ""
echo "Container created successfully!"
echo "Start the Container with: docker start breitbandmessung"
echo "View logs with: docker logs -f breitbandmessung"
echo "Files will be saved to: $PWD/messprotokolle"
echo ""
echo "Configuration file: $PWD/config/config.cfg"
echo "Edit this file to customize settings before starting the container"
echo ""

exit 0