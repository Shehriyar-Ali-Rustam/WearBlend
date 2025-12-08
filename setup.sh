#!/bin/bash

# WearBlend Setup Script
echo "=================================="
echo "  WearBlend Setup"
echo "=================================="

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=================================="
echo "  Setup Complete!"
echo "=================================="
echo ""
echo "To run the application:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the app:"
echo "     streamlit run app.py"
echo ""
echo "  3. Open http://localhost:8501 in your browser"
echo ""
