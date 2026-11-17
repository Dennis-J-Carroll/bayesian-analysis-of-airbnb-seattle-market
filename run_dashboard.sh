#!/bin/bash

# Seattle Airbnb Bayesian price model: launch the Streamlit app.
# Run from the project root. Use a Python 3.11 venv.

echo "Seattle Airbnb Bayesian price model"
echo "==================================="

if [ ! -f "app.py" ]; then
    echo "Error: app.py not found. Run this script from the project root."
    exit 1
fi

if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Streamlit not found. Installing requirements.txt..."
    pip install -r requirements.txt || { echo "Install failed. Run: pip install -r requirements.txt"; exit 1; }
fi

echo "Opening at http://localhost:8501 (Ctrl+C to stop)"
streamlit run app.py
