#!/bin/sh
cd "$(dirname "$0")" && exec python3 -m http.server "${1:-8080}" --bind 0.0.0.0
