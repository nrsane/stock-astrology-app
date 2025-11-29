#!/bin/bash
echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Download Swiss Ephemeris data
echo "📥 Downloading ephemeris data..."
python -c "import swisseph; swisseph.download_ephe()"

# Initialize database
echo "🗄️ Initializing database..."
python migrate_db.py

echo "✅ Build completed successfully!"
