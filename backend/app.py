from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, date
import os
import json

# Ensure ephemeris data is available
try:
    import swisseph as swe
    # Try to set ephemeris path, download if not available
    try:
        swe.set_ephe_path()
    except:
        print("Downloading ephemeris data...")
        swe.download_ephe()
        swe.set_ephe_path()
except ImportError:
    print("Swiss Ephemeris not available")

from database import init_db
from models.stock_models import db, Stock, BirthChart, HouseSignificator
from kp_astrology.chart_calculator import KPChartCalculator
from kp_astrology.significator import KPSignificator
from data.stock_data import StockDataManager

# Rest of the file remains the same...
