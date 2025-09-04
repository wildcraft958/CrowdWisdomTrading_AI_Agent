#!/bin/bash

# CrowdWisdom Trading AI Agent - Installation Script
# This script sets up the environment and installs dependencies

set -e  # Exit on any error

echo "🚀 CrowdWisdom Trading AI Agent - Installation Script"
echo "=================================================="

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
else
    echo "✅ Python $python_version detected"
fi

# Create virtual environment (optional but recommended)
echo ""
read -p "🔨 Create virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv crowdwisdom_env
    source crowdwisdom_env/bin/activate
    echo "✅ Virtual environment created and activated"
    echo "   To activate later: source crowdwisdom_env/bin/activate"
else
    echo "⚠️  Skipping virtual environment creation"
fi

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p output/reports
mkdir -p output/charts
mkdir -p data/cache
mkdir -p data/temp
echo "✅ Directories created"

# Set up environment file
echo ""
if [ ! -f "configs/.env" ]; then
    echo "⚙️  Setting up environment configuration..."
    cp configs/.env.example configs/.env
    echo "✅ Environment file created: configs/.env"
    echo "   Please edit this file with your API keys"
else
    echo "✅ Environment file already exists: configs/.env"
fi

# Run system test
echo ""
echo "🧪 Running system test..."
python3 test_system.py

# Final instructions
echo ""
echo "🎉 Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit configs/.env with your API keys:"
echo "   - OPENROUTER_API_KEY (required for LLM features)"
echo "   - SEC_IDENTITY (your email address)"
echo "   - Optional: TWINWORD_API_KEY, TWITTER_BEARER_TOKEN"
echo ""
echo "2. Run the analysis:"
echo "   python3 main.py"
echo ""
echo "3. For custom analysis:"
echo "   python3 -c \"from main import custom_analysis; print(custom_analysis(['AAPL'], ['@elonmusk']))\""
echo ""
echo "📚 Check README.md for detailed documentation"
echo "🐛 Run test_system.py to verify installation"
