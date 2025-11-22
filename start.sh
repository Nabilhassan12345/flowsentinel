#!/bin/bash

# ============================================================================
# FlowSentinel Quick Start Script
# ============================================================================
# This script helps you quickly start the FlowSentinel server
# ============================================================================

echo ""
echo "🧠 FlowSentinel - Quick Start"
echo "=============================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created (edit it to add your credentials)"
fi

echo ""
echo "🚀 Starting FlowSentinel server..."
echo ""
echo "📝 Note: Server will start at http://localhost:8000"
echo "📚 API Docs will be at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python main.py
