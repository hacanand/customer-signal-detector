#!/bin/bash
# Start the FastAPI backend in the background
echo "Starting FastAPI backend..."
cd /app/backend
# Bind to 127.0.0.1 since the frontend will proxy to it
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# Wait a moment to ensure the backend is up
sleep 2

# Start the Next.js frontend in the foreground
echo "Starting Next.js frontend..."
cd /app/frontend
# Use the PORT environment variable provided by Koyeb, fallback to 3000
export PORT="${PORT:-3000}"
npm run start -- -p $PORT
