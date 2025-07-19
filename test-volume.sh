#!/bin/bash

echo "Testing volume mapping..."
echo "Current directory: $PWD"
echo "Creating test directories..."

mkdir -p $PWD/config
mkdir -p $PWD/messprotokolle

echo "Test file content" > $PWD/messprotokolle/test.txt

echo "Running container to test volume mapping..."
docker run --rm -v $PWD/messprotokolle:/export:rw alpine:latest sh -c "
echo 'Container test file' > /export/container-test.txt
ls -la /export/
echo 'Files in /export:'
cat /export/test.txt 2>/dev/null || echo 'test.txt not found'
cat /export/container-test.txt 2>/dev/null || echo 'container-test.txt not found'
"

echo "Files in host messprotokolle directory:"
ls -la $PWD/messprotokolle/

echo "Volume mapping test completed."
rm $PWD/messprotokolle/*.txt