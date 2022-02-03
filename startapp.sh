#!/bin/bash
exec breitbandmessung --no-sandbox &
exec python3 /opt/click.py
