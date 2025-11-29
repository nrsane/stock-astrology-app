# Stock Astrology Analysis App

A web application that uses KP Astrology to analyze stock price movements based on planetary positions.

## Features

- 📊 Generate KP birth charts for stocks based on listing date/time
- 🏠 Identify house significators (2nd & 11th houses for wealth/gains)
- 📈 Correlate planetary transits with stock price movements
- 🌐 Web-based interface accessible from any device

## Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click the "Deploy to Render" button above
2. Connect your GitHub account
3. Select this repository
4. Render will automatically deploy your application

## Technology Stack

- **Backend**: Python Flask, SQLAlchemy, Swiss Ephemeris
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Database**: PostgreSQL (production), SQLite (development)
- **Deployment**: Render.com (free tier)

## API Endpoints

- `GET /` - Main application interface
- `GET /api/health` - Health check
- `POST /api/stocks` - Add new stock
- `GET /api/stocks` - List all stocks
- `GET /api/stocks/<symbol>` - Get stock details

## Example Usage

1. Add a stock like RELIANCE with listing date 2005-11-11 at 10:00 AM
2. View the generated birth chart and house significators
3. Analyze correlations between planetary movements and price changes

## Disclaimer

This application is for educational and research purposes only. Astrological stock analysis should not be considered financial advice.
