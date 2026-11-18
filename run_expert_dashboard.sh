#!/bin/bash

# Launch the app through the Streamlit Cloud entry point (expert_dashboard.py).
# Run from the project root.

echo "Seattle Airbnb Bayesian price model (cloud entry point)"

if ! command -v streamlit &> /dev/null; then
    echo "Streamlit not found. Installing requirements.txt..."
    pip install -r requirements.txt || { echo "Install failed."; exit 1; }
fi

echo "Opening at http://localhost:8501 (Ctrl+C to stop)"
streamlit run expert_dashboard.py --server.port=8501 --server.headless=true
