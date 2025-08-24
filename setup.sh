#!/bin/bash

echo "🚀 Setting up Sierra Agent..."
echo "================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -e .

echo "✅ Dependencies installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Please create one with your OpenAI API key:"
    echo "   cp config.template .env"
    echo "   # Then edit .env and add your OPENAI_API_KEY"
else
    echo "✅ Environment configuration found"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To get started:"
echo "1. Set your OpenAI API key in .env file"
echo "2. Run: python main.py"
echo "3. Or test the system: python test_system.py"
echo ""
echo "For help: python main.py --help"
