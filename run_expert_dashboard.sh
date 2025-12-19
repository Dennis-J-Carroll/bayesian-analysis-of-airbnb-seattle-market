#!/bin/bash

# Expert Dashboard Quick Start Script
# =====================================

echo "🏠 Seattle Airbnb Expert Dashboard"
echo "===================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Check if data exists
if [ ! -f "data/raw/listings.csv" ]; then
    echo "⚠️  Data file not found at data/raw/listings.csv"
    echo "   Please download the Seattle Airbnb data first."
    exit 1
fi

echo "✅ Data file found"
echo ""
echo "🚀 Launching Expert Dashboard..."
echo "   Opening at: http://localhost:8501"
echo ""
echo "📊 Available Pages:"
echo "   1. 🏠 Overview - Market statistics"
echo "   2. 🔍 Neighborhood Analysis - Deep dive"
echo "   3. 💰 Price Prediction - Bayesian inference"
echo "   4. 📈 Market Intelligence - Advanced analytics"
echo "   5. 🎯 Business Strategy - ROI analysis"
echo "   6. 🔬 Model Insights - Technical details"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Run the expert dashboard
streamlit run expert_dashboard.py --server.port=8501 --server.headless=true
