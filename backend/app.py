from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, date
import os
import json

# Handle ephemeris setup
def setup_ephemeris():
    """Setup Swiss Ephemeris data"""
    try:
        import swisseph as swe
        # Try to set ephemeris path
        try:
            swe.set_ephe_path()
            print("✅ Swiss Ephemeris initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️ Ephemeris setup failed: {e}")
            # Try to download ephemeris data
            try:
                print("📥 Downloading ephemeris data...")
                swe.download_ephe()
                swe.set_ephe_path()
                print("✅ Ephemeris data downloaded and initialized")
                return True
            except Exception as e2:
                print(f"❌ Failed to download ephemeris: {e2}")
                return False
    except ImportError as e:
        print(f"❌ Swiss Ephemeris not available: {e}")
        return False

# Initialize ephemeris
EPHEMERIS_AVAILABLE = setup_ephemeris()

from database import init_db
from models.stock_models import db, Stock, BirthChart, HouseSignificator

# Import KP astrology components with error handling
try:
    from kp_astrology.chart_calculator import KPChartCalculator
    from kp_astrology.significator import KPSignificator
    KP_AVAILABLE = True
except ImportError as e:
    print(f"❌ KP Astrology components not available: {e}")
    KP_AVAILABLE = False

from data.stock_data import StockDataManager

app = Flask(__name__)
CORS(app)

# Initialize managers with error handling
if KP_AVAILABLE and EPHEMERIS_AVAILABLE:
    chart_calculator = KPChartCalculator()
    significator_engine = KPSignificator()
else:
    chart_calculator = None
    significator_engine = None
    print("⚠️ KP Astrology features disabled due to missing dependencies")

stock_data_manager = StockDataManager()

# Initialize database
init_db(app)

# Rest of your routes remain the same...
        # Calculate birth chart (if dependencies available)
        if not chart_calculator or not significator_engine:
            db.session.rollback()
            return jsonify({
                'error': 'KP Astrology features not available. Required dependencies missing.'
            }), 500
        
        birth_chart_data = chart_calculator.calculate_stock_birth_chart(
            symbol, listing_date, listing_time_str
        )
