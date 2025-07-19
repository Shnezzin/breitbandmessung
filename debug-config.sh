#!/bin/bash

echo "=== Configuration Debug Script ==="
echo ""

echo "1. Checking config files..."
echo "config.cfg.defaults exists: $(test -f config.cfg.defaults && echo 'YES' || echo 'NO')"
echo "config/config.cfg exists: $(test -f config/config.cfg && echo 'YES' || echo 'NO')"

echo ""
echo "2. Content of config.cfg.defaults:"
if [ -f config.cfg.defaults ]; then
    cat config.cfg.defaults
else
    echo "File not found!"
fi

echo ""
echo "3. Content of config/config.cfg:"
if [ -f config/config.cfg ]; then
    cat config/config.cfg
else
    echo "File not found!"
fi

echo ""
echo "4. Testing config.shlib functions..."
if [ -f config.shlib ]; then
    source config.shlib
    echo "timezone: '$(config_get timezone General)'"
    echo "crontab: '$(config_get crontab General)'"
    echo "run_once: '$(config_get run_once General)'"
    echo "run_on_startup: '$(config_get run_on_startup General)'"
else
    echo "config.shlib not found!"
fi

echo ""
echo "5. Testing container config access..."
docker run --rm -v $PWD/config:/usr/src/app/config:ro breitbandmessung:latest sh -c "
echo 'Files in /usr/src/app/config:'
ls -la /usr/src/app/config/
echo ''
echo 'Content of config.cfg:'
cat /usr/src/app/config/config.cfg 2>/dev/null || echo 'File not found'
echo ''
echo 'Content of config.cfg.defaults:'
cat /usr/src/app/config.cfg.defaults 2>/dev/null || echo 'File not found'
"

echo ""
echo "=== Debug completed ==="