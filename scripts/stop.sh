#!/bin/bash

# FlowSentinel - Stop All Services
# This script stops both backend and frontend servers

echo "🛑 Stopping FlowSentinel services..."
echo ""

# Stop backend
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Stopping backend (port 8000)..."
    lsof -ti:8000 | xargs kill -9
    echo "✅ Backend stopped"
else
    echo "ℹ️  Backend not running"
fi

# Stop frontend
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "Stopping frontend (port 8080)..."
    lsof -ti:8080 | xargs kill -9
    echo "✅ Frontend stopped"
else
    echo "ℹ️  Frontend not running"
fi

echo ""
echo "✅ All services stopped"
