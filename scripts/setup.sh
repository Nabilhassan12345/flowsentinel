#!/bin/bash

# FlowSentinel Setup Script

echo "🧠 FlowSentinel Setup"
echo "===================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Remember to add your Slack webhook URL to .env"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  1. source venv/bin/activate"
echo "  2. python main.py"
echo ""
echo "To run the demo:"
echo "  1. Start the server (in one terminal)"
echo "  2. python demo.py (in another terminal)"
echo ""
echo "📚 Read README.md for more information"
