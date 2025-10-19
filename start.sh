#!/bin/bash

# Flow Highlight - Startup Script
# This script starts both the API server and frontend

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         Flow Highlight - Starting Servers                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first: python -m venv venv"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found!"
    echo "Please make sure you're in the correct directory"
    exit 1
fi

# Start API server in background
echo "🚀 Starting API server (port 8000)..."
source venv/bin/activate
python api_server.py > api_server.log 2>&1 &
API_PID=$!

# Save PID for cleanup
echo $API_PID > .api_server.pid

# Wait for API to be ready
echo "⏳ Waiting for API server to initialize (this may take 10-30 seconds)..."
sleep 10

# Check if API server is running
if ! ps -p $API_PID > /dev/null; then
    echo "❌ API server failed to start!"
    echo "Check api_server.log for details"
    exit 1
fi

echo "✓ API server started (PID: $API_PID)"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

# Start frontend
echo "🚀 Starting Next.js frontend (port 3000)..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Servers Running                           ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Frontend: http://localhost:3000                             ║"
echo "║  API:      http://localhost:8000                             ║"
echo "║  API Docs: http://localhost:8000/docs                        ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Press Ctrl+C to stop all servers                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    if [ -f "../.api_server.pid" ]; then
        API_PID=$(cat ../.api_server.pid)
        kill $API_PID 2>/dev/null
        rm ../.api_server.pid
        echo "✓ API server stopped"
    fi
    exit 0
}

# Set trap to catch Ctrl+C
trap cleanup INT TERM

# Start frontend (this will block)
npm run dev

# Cleanup if npm exits
cleanup

