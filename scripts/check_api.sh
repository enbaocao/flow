#!/bin/bash
# Quick health check for the API server

echo "Checking API server status..."
echo ""

# Check if server is responding
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ API server is running"
    echo ""
    echo "Health status:"
    curl -s http://localhost:8000/api/health | python3 -m json.tool
else
    echo "❌ API server is NOT responding"
    echo ""
    echo "Please start the API server:"
    echo "  source venv/bin/activate"
    echo "  python backend/api_server.py"
fi

