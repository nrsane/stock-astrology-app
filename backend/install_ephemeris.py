#!/usr/bin/env python3
"""
Script to download and install Swiss Ephemeris data
"""
import swisseph as swe

print("📥 Downloading Swiss Ephemeris data...")
try:
    swe.download_ephe()
    print("✅ Ephemeris data downloaded successfully!")
except Exception as e:
    print(f"❌ Failed to download ephemeris data: {e}")
