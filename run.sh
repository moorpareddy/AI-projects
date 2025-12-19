#!/bin/bash

# Resume Analyzer - Startup Script
# This script starts both backend and frontend servers

echo "╔═══════════════════════════════════════════════╗"
echo "║   Resume Analyzer & Job Matcher Startup      ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "📝 Copying .env.example to .env..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚡ Please edit .env and add your API keys"
    echo ""
    read -p "Press Enter after updating .env with your API keys..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting servers..."
echo ""

# Start backend in background
echo "🔧 Starting Backend API (FastAPI)..."
python -m backend.main &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Backend URL: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""

# Wait for backend to start
sleep 5

# Start frontend
echo "🎨 Starting Frontend (Streamlit)..."
echo "   Frontend URL: http://localhost:8501"
echo ""
streamlit run frontend/app.py &
FRONTEND_PID=$!

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║          ✅ All Services Started!             ║"
echo "╠═══════════════════════════════════════════════╣"
echo "║  Backend:  http://localhost:8000              ║"
echo "║  API Docs: http://localhost:8000/docs         ║"
echo "║  Frontend: http://localhost:8501              ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "📌 Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Shutting down...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
