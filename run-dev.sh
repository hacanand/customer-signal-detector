#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting Backend..."
(cd "${ROOT_DIR}/backend" && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!

echo "Starting Frontend..."
(cd "${ROOT_DIR}/frontend" && npm run dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

wait
