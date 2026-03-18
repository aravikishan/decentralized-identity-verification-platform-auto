#!/bin/bash
set -e
echo "Starting Decentralized Identity Verification Platform..."
uvicorn app:app --host 0.0.0.0 --port 9020 --workers 1
