#!/bin/bash
set -e

# Get PORT from environment variable (Cloud Run sets this)
PORT=${PORT:-8080}

echo "Starting Air Drums on port $PORT"

# Start gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app:app


