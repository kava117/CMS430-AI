#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/sunzi/backend"
FRONTEND_DIR="$SCRIPT_DIR/sunzi/frontend"

# Kill any existing instances on these ports
echo "Clearing ports 5000 and 5173..."
lsof -ti:5000,5173 | xargs kill -9 2>/dev/null || true

# Start Flask backend
echo "Starting Flask backend on port 5000..."
cd "$BACKEND_DIR"
python app.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!

# Wait for Flask to be ready
for i in $(seq 1 20); do
  if curl -s http://localhost:5000/api/state/ping > /dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

# Start Vite frontend
echo "Starting Vite frontend on port 5173..."
cd "$FRONTEND_DIR"
npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/vite.log 2>&1 &
VITE_PID=$!

# Wait for Vite to be ready
for i in $(seq 1 20); do
  if curl -s http://localhost:5173 > /dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

# Expose ports via GitHub Codespaces
echo "Exposing ports..."
gh codespace ports visibility 5000:public 2>/dev/null || true
gh codespace ports visibility 5173:public 2>/dev/null || true

echo ""
echo "SUNZI is running."
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop."

# On exit, kill both servers
trap "echo 'Stopping...'; kill $FLASK_PID $VITE_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait
