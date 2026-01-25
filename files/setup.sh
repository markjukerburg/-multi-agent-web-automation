#!/bin/bash

# Multi-Agent Web Automation System
# Setup Script

set -e  # Exit on error

echo "=================================="
echo "Multi-Agent Web Automation System"
echo "Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11 or higher required. Found: $python_version"
    exit 1
fi
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip
echo "✓ pip upgraded"

# Install requirements
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium
echo "✓ Playwright browsers installed"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p screenshots
mkdir -p debug_screenshots
echo "✓ Directories created"

# Check for API keys
echo ""
echo "Checking for API keys..."
if [ ! -f ".env" ]; then
    echo "Creating .env file template..."
    cat > .env << EOF
# API Keys
# Uncomment and add your keys

# OpenAI API Key (for GPT-4 Vision)
# OPENAI_API_KEY=your-openai-key-here

# Anthropic API Key (for Claude)
# ANTHROPIC_API_KEY=your-anthropic-key-here

# Configuration
# PROVIDER=openai  # or anthropic
EOF
    echo "✓ .env template created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
else
    echo "✓ .env file already exists"
fi

# Check if API keys are set
if grep -q "your-openai-key-here" .env 2>/dev/null || grep -q "your-anthropic-key-here" .env 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: API keys not configured!"
    echo "Please edit .env and add your API keys before running the system."
fi

# Run a quick test
echo ""
echo "Running quick validation test..."
python3 -c "
import sys
try:
    import playwright
    import openai
    import anthropic
    import pydantic
    print('✓ All core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

echo ""
echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run an example: python examples.py 1"
echo "3. Or use the system: python main.py"
echo ""
echo "Documentation: See README.md"
echo "Examples: See examples.py"
echo ""
