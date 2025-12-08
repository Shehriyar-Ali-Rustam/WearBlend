#!/bin/bash

# WearBlend Run Script
echo "Starting WearBlend..."

# Check if venv exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Streamlit
streamlit run app.py --server.port 8501 --server.address localhost
