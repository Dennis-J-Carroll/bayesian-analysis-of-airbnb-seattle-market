#!/bin/bash

# Seattle Airbnb Dashboard Launcher
# Quick script to launch the Streamlit dashboard

echo "🏠 Seattle Airbnb Pricing & Investment Dashboard"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "dashboard/app.py" ]; then
    echo "❌ Error: dashboard/app.py not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check if data files exist
if [ ! -f "data/raw/listings.csv" ]; then
    echo "⚠️  Warning: data/raw/listings.csv not found!"
    echo "The dashboard requires this data file to run."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Streamlit not found. Installing dependencies..."
    pip install -r requirements-dashboard.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        echo "Please run: pip install -r requirements-dashboard.txt"
        exit 1
    fi
fi

echo "✅ Dependencies OK"
echo ""
echo "🚀 Launching dashboard..."
echo ""
echo "📍 The dashboard will open at: http://localhost:8501"
echo "🛑 To stop the dashboard, press Ctrl+C"
echo ""
echo "⏳ First launch will take 2-3 minutes to fit the model..."
echo "   Subsequent launches will be instant (cached)."
echo ""

# Launch Streamlit
streamlit run dashboard/app.py
