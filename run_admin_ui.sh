#!/bin/bash
# Launch Admin UI with virtual environment Python
# This ensures all dependencies are available

cd "$(dirname "$0")"

# Activate virtual environment and run admin UI
if [ -d ".venv" ]; then
    echo "🔧 Using virtual environment..."
    .venv/bin/python -m streamlit run agents_capstone/admin_ui.py
else
    echo "⚠️  Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m streamlit run agents_capstone/admin_ui.py
fi
