#!/bin/bash

echo "🚀 Starting build process for Stock Astrology App..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download Swiss Ephemeris data
echo "📥 Downloading Swiss Ephemeris data..."
python -c "import swisseph; swisseph.download_ephe()"

# Initialize database
echo "🗄️ Initializing database..."
python migrate_db.py

echo "✅ Build completed successfully!"
