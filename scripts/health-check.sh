#!/usr/bin/env bash
set -e
URL="${1:-http://localhost:8080/health}"
echo "Checking $URL ..."
curl -fsS "$URL" && echo "OK" || (echo "FAILED" && exit 1)
