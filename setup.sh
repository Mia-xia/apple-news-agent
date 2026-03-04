#!/bin/bash
# Setup script for Apple News Monitoring Agent

set -e

echo "========================================="
echo "Apple News Monitoring Agent - Setup"
echo "========================================="
echo ""

# Check Python version
echo "📦 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env configuration file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys and email credentials"
    echo ""
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit your configuration:"
echo "   nano .env"
echo ""
echo "2. Test the agent (fetch news without sending):"
echo "   python3 agent.py --test"
echo ""
echo "3. Run once:"
echo "   python3 agent.py --once"
echo ""
echo "4. Run on daily schedule:"
echo "   python3 agent.py"
echo ""
echo "For detailed instructions, see README.md"
echo ""
