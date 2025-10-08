#!/bin/bash

# Schedulyze - Quick Start Script
# This script helps you quickly start the Schedulyze application

echo "🎓 Schedulyze - AI-Powered Study Scheduler"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "schedulyze_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv schedulyze_env
    echo "✅ Virtual environment created!"
fi

# Activate virtual environment and install dependencies
echo "📋 Installing dependencies..."
./schedulyze_env/bin/pip install -r requirements.txt > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Error installing dependencies. Check requirements.txt"
    exit 1
fi

echo ""
echo "🚀 Starting Schedulyze..."
echo "📱 Open your browser and go to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start the Streamlit app
./schedulyze_env/bin/streamlit run app.py