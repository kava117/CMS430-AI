#!/usr/bin/env bash
# Sokoban Solver - Startup Script
# Usage: ./start.sh

set -e

cd "$(dirname "$0")"

echo "=== Sokoban Solver ==="
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "Done."
echo ""

# Run tests
echo "Running tests..."
if python -m pytest tests/ -q; then
    echo ""
    echo "All tests passed!"
else
    echo ""
    echo "WARNING: Some tests failed. The app may still run."
fi
echo ""

# Start the web server
echo "Starting web server on http://localhost:5000"
echo "Press Ctrl+C to stop."
echo ""
python -m flask --app web.app run --host 0.0.0.0 --port 5000
