#!/bin/bash
# 🚀 Quick Demo Runner
# Run this script to execute the complete FlowSentinel demo

echo "🎭 FlowSentinel Demo Runner"
echo "=========================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Server is not running!"
    echo ""
    echo "Please start the server first:"
    echo "  python src/main.py"
    echo ""
    exit 1
fi

echo "✅ Server is running"
echo ""

# Activate virtual environment if needed
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the demo
echo "🎬 Starting demo..."
echo ""
python demo.py

echo ""
echo "✅ Demo complete!"
echo ""
echo "📱 Check your Slack for the alert!"
echo "🌐 Visit http://localhost:8000/docs for API documentation"
echo ""
