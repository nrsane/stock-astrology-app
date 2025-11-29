from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///stocks.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# Stock Data Manager for fetching real price data
class StockDataManager:
    def __init__(self):
        pass
    
    def fetch_stock_data(self, symbol, period="2y"):
        """Fetch stock data from Yahoo Finance for NSE stocks"""
        try:
            import yfinance as yf
            import pandas as pd
            
            # NSE symbols have .NS suffix
            yf_symbol = f"{symbol}.NS"
            stock = yf.Ticker(yf_symbol)
            hist_data = stock.history(period=period)
            
            if hist_data.empty:
                return None
                
            return hist_data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def store_stock_prices(self, stock_id, hist_data):
        """Store historical prices in database"""
        try:
            for date, row in hist_data.iterrows():
                # Check if record already exists
                existing = StockPrice.query.filter_by(
                    stock_id=stock_id, 
                    date=date.date()
                ).first()
                
                if not existing and not pd.isna(row['Close']):
                    stock_price = StockPrice(
                        stock_id=stock_id,
                        date=date.date(),
                        open_price=float(row['Open']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        close_price=float(row['Close']),
                        volume=int(row['Volume']) if pd.notna(row['Volume']) else 0
                    )
                    db.session.add(stock_price)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error storing prices: {e}")
            return False

# Initialize stock data manager
stock_data_manager = StockDataManager()
# Define ALL models first, before any relationships

class Stock(db.Model):
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    listing_date = db.Column(db.String(50), nullable=False)
    listing_time = db.Column(db.String(50), default='10:00')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships will be defined after all models are declared
    birth_charts = db.relationship('BirthChart', backref='stock', lazy=True, cascade="all, delete-orphan")
    house_significators = db.relationship('HouseSignificator', backref='stock', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'listing_date': self.listing_date,
            'listing_time': self.listing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BirthChart(db.Model):
    __tablename__ = 'birth_charts'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    ascendant_degree = db.Column(db.Float)
    planet_positions = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HouseSignificator(db.Model):
    __tablename__ = 'house_significators'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    house_number = db.Column(db.Integer, nullable=False)
    cuspal_sign_lord = db.Column(db.String(20))
    cuspal_star_lord = db.Column(db.String(20))
    cuspal_sub_lord = db.Column(db.String(20))
    all_significators = db.Column(db.JSON)

class StockPrice(db.Model):
    __tablename__ = 'stock_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'open': self.open_price,
            'high': self.high_price,
            'low': self.low_price,
            'close': self.close_price,
            'volume': self.volume
        }
# Now create tables after all models are defined
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully!")
        print("✅ Tables created: stocks, birth_charts, house_significators")
    except Exception as e:
        print(f"❌ Database creation error: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    try:
        # Test database connection
        stock_count = Stock.query.count()
        return jsonify({
            "status": "healthy",
            "message": "Stock Astrology App with Database",
            "database": "connected",
            "stocks_count": stock_count,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "message": "Database connection issue",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# Stock Management API
@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    try:
        stocks = Stock.query.all()
        return jsonify({
            'success': True,
            'stocks': [stock.to_dict() for stock in stocks],
            'count': len(stocks)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    try:
        data = request.get_json()
        
        if not data or not data.get('symbol'):
            return jsonify({'success': False, 'error': 'Stock symbol is required'}), 400
        
        symbol = data['symbol'].upper().strip()
        listing_date = data.get('listing_date', '2000-01-01')
        listing_time = data.get('listing_time', '10:00')
        
        # Check if stock already exists
        existing_stock = Stock.query.filter_by(symbol=symbol).first()
        if existing_stock:
            return jsonify({
                'success': False, 
                'error': f'Stock {symbol} already exists'
            }), 400
        
        # Create new stock
        new_stock = Stock(
            symbol=symbol,
            name=data.get('name', f'{symbol} Company'),
            listing_date=listing_date,
            listing_time=listing_time
        )
        
        db.session.add(new_stock)
        db.session.flush()  # Get the ID without committing
        
        # Create basic birth chart
        birth_chart = BirthChart(
            stock_id=new_stock.id,
            ascendant_degree=0.0,
            planet_positions={
                "status": "KP calculations coming soon",
                "planets": ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
            }
        )
        db.session.add(birth_chart)
        
        # Create house significators for 2nd and 11th houses
        for house_num in [2, 11]:
            house_name = "Wealth" if house_num == 2 else "Gains"
            significator = HouseSignificator(
                stock_id=new_stock.id,
                house_number=house_num,
                cuspal_sign_lord="Mars",
                cuspal_star_lord="Venus", 
                cuspal_sub_lord="Mercury",
                all_significators=["Mars", "Venus", "Mercury", "Jupiter"]
            )
            db.session.add(significator)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Stock {symbol} added successfully with KP chart!',
            'stock': new_stock.to_dict(),
            'kp_status': 'Basic KP chart created - Real calculations coming soon'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/<symbol>', methods=['GET'])
def get_stock(symbol):
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        birth_chart = BirthChart.query.filter_by(stock_id=stock.id).first()
        house_significators = HouseSignificator.query.filter_by(stock_id=stock.id).all()
        
        return jsonify({
            'success': True,
            'stock': stock.to_dict(),
            'birth_chart': {
                'ascendant_degree': birth_chart.ascendant_degree if birth_chart else None,
                'planet_positions': birth_chart.planet_positions if birth_chart else None
            },
            'house_significators': [
                {
                    'house_number': hs.house_number,
                    'house_name': 'Wealth (2nd)' if hs.house_number == 2 else 'Gains (11th)',
                    'cuspal_sign_lord': hs.cuspal_sign_lord,
                    'cuspal_star_lord': hs.cuspal_star_lord,
                    'cuspal_sub_lord': hs.cuspal_sub_lord,
                    'all_significators': hs.all_significators
                } for hs in house_significators
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    try:
        stock = Stock.query.get(stock_id)
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        db.session.delete(stock)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Stock {stock.symbol} deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# KP Astrology API Endpoints
@app.route('/api/kp/calculate/<symbol>', methods=['POST'])
def calculate_kp_chart(symbol):
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        # Simulate KP calculations
        import random
        ascendant = round(random.uniform(0, 360), 2)
        
        # Update birth chart with simulated data
        birth_chart = BirthChart.query.filter_by(stock_id=stock.id).first()
        if birth_chart:
            birth_chart.ascendant_degree = ascendant
            birth_chart.planet_positions = {
                "ascendant": ascendant,
                "planets": {
                    "Sun": round(random.uniform(0, 360), 2),
                    "Moon": round(random.uniform(0, 360), 2),
                    "Mars": round(random.uniform(0, 360), 2),
                    "Mercury": round(random.uniform(0, 360), 2),
                    "Jupiter": round(random.uniform(0, 360), 2),
                    "Venus": round(random.uniform(0, 360), 2),
                    "Saturn": round(random.uniform(0, 360), 2),
                    "Rahu": round(random.uniform(0, 360), 2),
                    "Ketu": round(random.uniform(0, 360), 2)
                },
                "calculation_time": datetime.utcnow().isoformat()
            }
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Simulated KP chart calculated for {symbol}',
            'ascendant': ascendant,
            'status': 'Simulated data - Real Swiss Ephemeris coming soon'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# KP Astrology Correlation Engine
class KPCorrelationEngine:
    def __init__(self):
        self.planet_influences = {
            'Sun': {'nature': 'benefic', 'house_2_weight': 0.7, 'house_11_weight': 0.6},
            'Moon': {'nature': 'benefic', 'house_2_weight': 0.8, 'house_11_weight': 0.7},
            'Mars': {'nature': 'malefic', 'house_2_weight': -0.6, 'house_11_weight': -0.5},
            'Mercury': {'nature': 'neutral', 'house_2_weight': 0.5, 'house_11_weight': 0.6},
            'Jupiter': {'nature': 'benefic', 'house_2_weight': 0.9, 'house_11_weight': 0.8},
            'Venus': {'nature': 'benefic', 'house_2_weight': 0.8, 'house_11_weight': 0.9},
            'Saturn': {'nature': 'malefic', 'house_2_weight': -0.7, 'house_11_weight': -0.6},
            'Rahu': {'nature': 'malefic', 'house_2_weight': -0.5, 'house_11_weight': -0.4},
            'Ketu': {'nature': 'malefic', 'house_2_weight': -0.5, 'house_11_weight': -0.4}
        }
    
    def calculate_daily_score(self, house_significators, price_change):
        """Calculate daily astrological score based on house significators"""
        daily_score = 0
        
        for significator in house_significators:
            planet = significator['cuspal_sign_lord']
            house_num = significator['house_number']
            
            if planet in self.planet_influences:
                influence = self.planet_influences[planet]
                weight = influence[f'house_{house_num}_weight']
                daily_score += weight
        
        return daily_score
    
    def analyze_correlation(self, stock_id, days=90):
        """Analyze correlation between KP factors and price movements"""
        try:
            # Get stock prices for last N days
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            prices = StockPrice.query.filter(
                StockPrice.stock_id == stock_id,
                StockPrice.date >= start_date
            ).order_by(StockPrice.date).all()
            
            if len(prices) < 10:
                return {'error': 'Insufficient price data'}
            
            # Get house significators
            house_significators = HouseSignificator.query.filter_by(stock_id=stock_id).all()
            house_data = [
                {
                    'house_number': hs.house_number,
                    'cuspal_sign_lord': hs.cuspal_sign_lord,
                    'cuspal_star_lord': hs.cuspal_star_lord,
                    'cuspal_sub_lord': hs.cuspal_sub_lord,
                    'all_significators': hs.all_significators
                } for hs in house_significators
            ]
            
            # Calculate daily correlations
            analysis_data = []
            for i in range(1, len(prices)):
                price_today = prices[i]
                price_yesterday = prices[i-1]
                
                price_change = ((price_today.close_price - price_yesterday.close_price) / 
                              price_yesterday.close_price) * 100
                
                daily_score = self.calculate_daily_score(house_data, price_change)
                
                analysis_data.append({
                    'date': price_today.date.isoformat(),
                    'price': price_today.close_price,
                    'price_change_percent': round(price_change, 2),
                    'astrology_score': round(daily_score, 2),
                    'direction_match': (daily_score > 0 and price_change > 0) or 
                                     (daily_score < 0 and price_change < 0)
                })
            
            # Calculate overall correlation
            matches = sum(1 for data in analysis_data if data['direction_match'])
            accuracy = round((matches / len(analysis_data)) * 100, 2) if analysis_data else 0
            
            return {
                'analysis_period': f'{start_date} to {end_date}',
                'total_days_analyzed': len(analysis_data),
                'prediction_accuracy': accuracy,
                'daily_analysis': analysis_data[-10:],  # Last 10 days
                'key_insights': self.generate_insights(analysis_data, house_data)
            }
            
        except Exception as e:
            return {'error': f'Correlation analysis failed: {str(e)}'}
    
    def generate_insights(self, analysis_data, house_data):
        """Generate insights from correlation analysis"""
        insights = []
        
        if not analysis_data:
            return insights
        
        # Calculate average metrics
        avg_accuracy = sum(1 for d in analysis_data if d['direction_match']) / len(analysis_data)
        
        if avg_accuracy > 0.6:
            insights.append("Strong correlation between KP factors and price movements")
        elif avg_accuracy > 0.5:
            insights.append("Moderate correlation observed")
        else:
            insights.append("Weak correlation - needs more analysis")
        
        # Planet-specific insights
        planet_performance = {}
        for data in analysis_data:
            for house in house_data:
                planet = house['cuspal_sign_lord']
                if data['direction_match']:
                    planet_performance[planet] = planet_performance.get(planet, 0) + 1
        
        if planet_performance:
            best_planet = max(planet_performance, key=planet_performance.get)
            insights.append(f"Most influential planet: {best_planet}")
        
        return insights

# Initialize correlation engine
kp_correlation_engine = KPCorrelationEngine()
# Database reset endpoint (for development)
@app.route('/api/reset-db', methods=['POST'])
def reset_database():
    try:
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        return jsonify({
            'success': True,
            'message': 'Database reset successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
# Stock Price Data Routes
@app.route('/api/stocks/<symbol>/fetch-prices', methods=['POST'])
def fetch_stock_prices(symbol):
    """Fetch and store current stock prices"""
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        # Fetch data from Yahoo Finance
        hist_data = stock_data_manager.fetch_stock_data(symbol, period="1y")
        
        if hist_data is None:
            return jsonify({'success': False, 'error': 'Failed to fetch stock data'}), 500
        
        # Store in database
        success = stock_data_manager.store_stock_prices(stock.id, hist_data)
        
        if success:
            price_count = StockPrice.query.filter_by(stock_id=stock.id).count()
            return jsonify({
                'success': True,
                'message': f'Stock prices fetched and stored for {symbol}',
                'price_records': price_count,
                'period': '1 year'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to store price data'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/<symbol>/prices', methods=['GET'])
def get_stock_prices(symbol):
    """Get stock price data"""
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        # Get date range from query parameters
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        prices = StockPrice.query.filter(
            StockPrice.stock_id == stock.id,
            StockPrice.date >= start_date
        ).order_by(StockPrice.date).all()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'prices': [price.to_dict() for price in prices],
            'period': f'{start_date} to {end_date}',
            'count': len(prices)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# KP Correlation Analysis Routes
@app.route('/api/stocks/<symbol>/correlation', methods=['GET'])
def get_correlation_analysis(symbol):
    """Get correlation analysis between KP factors and price movements"""
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        days = request.args.get('days', 90, type=int)
        analysis = kp_correlation_engine.analyze_correlation(stock.id, days)
        
        if 'error' in analysis:
            return jsonify({'success': False, 'error': analysis['error']}), 500
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'correlation_analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Prediction Engine Route
@app.route('/api/stocks/<symbol>/predict', methods=['POST'])
def predict_stock_movement(symbol):
    """Predict stock movement based on KP astrology"""
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        data = request.get_json()
        prediction_date_str = data.get('date', datetime.utcnow().date().isoformat())
        
        # Simple prediction based on house significators
        house_significators = HouseSignificator.query.filter_by(stock_id=stock.id).all()
        
        prediction_score = 0
        factors = []
        
        for hs in house_significators:
            planet = hs.cuspal_sign_lord
            if planet in kp_correlation_engine.planet_influences:
                influence = kp_correlation_engine.planet_influences[planet]
                weight = influence[f'house_{hs.house_number}_weight']
                prediction_score += weight
                factors.append(f"{planet} in house {hs.house_number}: {weight}")
        
        # Determine prediction
        if prediction_score > 0.5:
            prediction = "BULLISH"
            confidence = "HIGH"
        elif prediction_score > 0:
            prediction = "SLIGHTLY BULLISH" 
            confidence = "MEDIUM"
        elif prediction_score > -0.5:
            prediction = "SLIGHTLY BEARISH"
            confidence = "MEDIUM"
        else:
            prediction = "BEARISH"
            confidence = "HIGH"
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'prediction_date': prediction_date_str,
            'prediction': prediction,
            'confidence': confidence,
            'prediction_score': round(prediction_score, 2),
            'factors_considered': factors,
            'note': 'Based on current house significators and planetary influences'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
