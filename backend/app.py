from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, date
import os
import json

from database import init_db
from models.stock_models import db, Stock, BirthChart, HouseSignificator
from kp_astrology.chart_calculator import KPChartCalculator
from kp_astrology.significator import KPSignificator
from data.stock_data import StockDataManager

app = Flask(__name__)
CORS(app)

# Initialize database
init_db(app)

# Initialize managers
chart_calculator = KPChartCalculator()
significator_engine = KPSignificator()
stock_data_manager = StockDataManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    """Add a new stock with listing details"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        listing_date_str = data.get('listing_date')
        listing_time_str = data.get('listing_time', '10:00')
        
        if not symbol or not listing_date_str:
            return jsonify({'error': 'Symbol and listing date are required'}), 400
        
        # Parse dates
        listing_date = datetime.strptime(listing_date_str, '%Y-%m-%d').date()
        listing_time = datetime.strptime(listing_time_str, '%H:%M').time()
        
        # Check if stock already exists
        existing_stock = Stock.query.filter_by(symbol=symbol).first()
        if existing_stock:
            return jsonify({'error': f'Stock {symbol} already exists'}), 400
        
        # Create new stock
        stock = Stock(
            symbol=symbol,
            listing_date=listing_date,
            listing_time=listing_time
        )
        db.session.add(stock)
        db.session.flush()  # Get the ID without committing
        
        # Calculate birth chart
        birth_chart_data = chart_calculator.calculate_stock_birth_chart(
            symbol, listing_date, listing_time_str
        )
        
        if not birth_chart_data:
            db.session.rollback()
            return jsonify({'error': 'Failed to calculate birth chart'}), 500
        
        # Store birth chart
        birth_chart = BirthChart(
            stock_id=stock.id,
            ascendant_degree=birth_chart_data['ascendant'],
            cusps=birth_chart_data['cusps'],
            planet_positions=birth_chart_data['planets'],
            house_positions=birth_chart_data['house_positions']
        )
        db.session.add(birth_chart)
        
        # Calculate and store significators for 2nd and 11th houses
        for house_num in [2, 11]:
            significators = significator_engine.find_house_significators(birth_chart_data, house_num)
            if significators:
                house_sig = HouseSignificator(
                    stock_id=stock.id,
                    house_number=house_num,
                    cuspal_sign_lord=significators['cuspal_sign_lord'],
                    cuspal_star_lord=significators['cuspal_star_lord'],
                    cuspal_sub_lord=significators['cuspal_sub_lord'],
                    occupying_planets=significators['occupying_planets'],
                    all_significators=significators['all_significators']
                )
                db.session.add(house_sig)
        
        db.session.commit()
        
        # Fetch initial stock data in background (non-blocking)
        try:
            hist_data = stock_data_manager.fetch_stock_data(symbol, period="1y")
            if hist_data is not None:
                stock_data_manager.store_stock_prices(stock.id, hist_data)
        except Exception as e:
            print(f"Background price fetch failed: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Stock {symbol} added successfully',
            'stock_id': stock.id,
            'birth_chart': birth_chart_data,
            'significators': {
                'second_house': significator_engine.find_house_significators(birth_chart_data, 2),
                'eleventh_house': significator_engine.find_house_significators(birth_chart_data, 11)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks', methods=['GET'])
def get_all_stocks():
    """Get all stocks in database"""
    try:
        stocks = Stock.query.all()
        stocks_data = []
        
        for stock in stocks:
            stocks_data.append({
                'id': stock.id,
                'symbol': stock.symbol,
                'listing_date': stock.listing_date.isoformat(),
                'listing_time': stock.listing_time.strftime('%H:%M'),
                'created_at': stock.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'stocks': stocks_data,
            'count': len(stocks_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/<symbol>', methods=['GET'])
def get_stock(symbol):
    """Get stock details with birth chart and significators"""
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'error': f'Stock {symbol} not found'}), 404
        
        birth_chart = BirthChart.query.filter_by(stock_id=stock.id).first()
        house_significators = HouseSignificator.query.filter_by(stock_id=stock.id).all()
        
        return jsonify({
            'success': True,
            'stock': {
                'id': stock.id,
                'symbol': stock.symbol,
                'listing_date': stock.listing_date.isoformat(),
                'listing_time': stock.listing_time.strftime('%H:%M'),
                'created_at': stock.created_at.isoformat()
            },
            'birth_chart': {
                'ascendant_degree': birth_chart.ascendant_degree,
                'cusps': birth_chart.cusps,
                'planet_positions': birth_chart.planet_positions,
                'house_positions': birth_chart.house_positions
            } if birth_chart else None,
            'house_significators': [
                {
                    'house_number': hs.house_number,
                    'cuspal_sign_lord': hs.cuspal_sign_lord,
                    'cuspal_star_lord': hs.cuspal_star_lord,
                    'cuspal_sub_lord': hs.cuspal_sub_lord,
                    'occupying_planets': hs.occupying_planets,
                    'all_significators': hs.all_significators
                } for hs in house_significators
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/<int:stock_id>/prices', methods=['GET'])
def get_stock_prices(stock_id):
    """Get stock price data"""
    try:
        from datetime import timedelta
        
        # Get date range from query parameters
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        price_data = stock_data_manager.get_price_correlation_data(
            stock_id, start_date, end_date
        )
        
        return jsonify({
            'success': True,
            'stock_id': stock_id,
            'price_data': price_data,
            'period': f'{start_date.date()} to {end_date.date()}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
