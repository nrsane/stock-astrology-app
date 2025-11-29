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

# Stock Model
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    listing_date = db.Column(db.String(50), nullable=False)
    listing_time = db.Column(db.String(50), default='10:00')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'listing_date': self.listing_date,
            'listing_time': self.listing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Birth Chart Model (for KP Astrology)
class BirthChart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    ascendant_degree = db.Column(db.Float)
    planet_positions = db.Column(db.JSON)  # Store planet data as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# House Significators Model
class HouseSignificator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    house_number = db.Column(db.Integer, nullable=False)
    cuspal_sign_lord = db.Column(db.String(20))
    cuspal_star_lord = db.Column(db.String(20))
    cuspal_sub_lord = db.Column(db.String(20))
    all_significators = db.Column(db.JSON)  # Store as JSON list

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Stock Astrology App with Database",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    })

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
        db.session.commit()
        
        # Create basic birth chart (simplified for now)
        birth_chart = BirthChart(
            stock_id=new_stock.id,
            ascendant_degree=0.0,  # Will calculate with real KP later
            planet_positions={"status": "KP calculations coming soon"}
        )
        db.session.add(birth_chart)
        
        # Create house significators for 2nd and 11th houses
        for house_num in [2, 11]:
            significator = HouseSignificator(
                stock_id=new_stock.id,
                house_number=house_num,
                cuspal_sign_lord="Mars",  # Placeholder
                cuspal_star_lord="Venus",  # Placeholder
                cuspal_sub_lord="Mercury",  # Placeholder
                all_significators=["Mars", "Venus", "Mercury"]  # Placeholder
            )
            db.session.add(significator)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Stock {symbol} added successfully with KP chart!',
            'stock': new_stock.to_dict(),
            'kp_status': 'Basic chart created - Full KP calculations coming soon'
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
            } if birth_chart else None,
            'house_significators': [
                {
                    'house_number': hs.house_number,
                    'cuspal_sign_lord': hs.cuspal_sign_lord,
                    'cuspal_star_lord': hs.cuspal_star_lord,
                    'cuspal_sub_lord': hs.cuspal_sub_lord,
                    'all_significators': hs.all_significators
                } for hs in house_significators
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# KP Astrology API Endpoints
@app.route('/api/kp/calculate/<symbol>', methods=['POST'])
def calculate_kp_chart(symbol):
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        # Placeholder for KP calculations
        # In next step, we'll add real Swiss Ephemeris calculations
        
        return jsonify({
            'success': True,
            'message': f'KP chart calculation initiated for {symbol}',
            'status': 'Real KP calculations coming in next update',
            'next_step': 'Will integrate Swiss Ephemeris for accurate planetary positions'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
