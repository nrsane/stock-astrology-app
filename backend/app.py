from flask import Flask, jsonify, request
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
    __tablename__ = 'stocks'
    
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

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stock Astrology App</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 15px;
                color: #333;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .phase {
                background: #e3f2fd;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #2196f3;
            }
            .phase.completed {
                background: #d4edda;
                border-left-color: #28a745;
            }
            .form-group { margin: 15px 0; }
            input, button { 
                padding: 10px; 
                margin: 5px; 
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button { background: #667eea; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Stock Astrology App</h1>
            
            <div class="phase completed">
                <h2>✅ PHASE 2: DATABASE DEPLOYED</h2>
                <p><strong>Database + Stock Management Ready!</strong></p>
            </div>

            <div class="phase">
                <h3>📊 Add New Stock</h3>
                <form onsubmit="addStock(event)">
                    <div class="form-group">
                        <input type="text" id="symbol" placeholder="Stock Symbol (e.g., RELIANCE)" required>
                    </div>
                    <div class="form-group">
                        <input type="date" id="listingDate" required>
                        <input type="time" id="listingTime" value="10:00">
                    </div>
                    <button type="submit">Add Stock</button>
                </form>
                <div id="result" style="margin-top: 10px;"></div>
            </div>

            <div class="phase">
                <h3>📋 Deployment Progress</h3>
                <p><strong>Phase 1:</strong> ✅ Basic Flask App</p>
                <p><strong>Phase 2:</strong> ✅ Database + Stock Management (Current)</p>
                <p><strong>Phase 3:</strong> ➡️ Real Stock Price Data</p>
                <p><strong>Phase 4:</strong> ➡️ KP Astrology & Correlation</p>
            </div>

            <div style="margin-top: 30px;">
                <h3>🔧 API Endpoints</h3>
                <p><a href="/api/health" style="color: #667eea;">/api/health</a> - Health Check</p>
                <p><a href="/api/stocks" style="color: #667eea;">/api/stocks</a> - List Stocks</p>
                <p><a href="/api/phase3-prepare" style="color: #667eea;">/api/phase3-prepare</a> - Prepare Phase 3</p>
            </div>
        </div>

        <script>
            document.getElementById('listingDate').valueAsDate = new Date();
            
            async function addStock(e) {
                e.preventDefault();
                const symbol = document.getElementById('symbol').value;
                const listingDate = document.getElementById('listingDate').value;
                const listingTime = document.getElementById('listingTime').value;
                
                try {
                    const response = await fetch('/api/stocks', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({symbol, listing_date: listingDate, listing_time: listingTime})
                    });
                    const data = await response.json();
                    
                    const result = document.getElementById('result');
                    if (data.success) {
                        result.innerHTML = `<div style="color: green;">✅ ${data.message}</div>`;
                        document.getElementById('symbol').value = '';
                    } else {
                        result.innerHTML = `<div style="color: red;">❌ ${data.error}</div>`;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `<div style="color: red;">❌ Network error</div>`;
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/health')
def health_check():
    stock_count = Stock.query.count()
    return jsonify({
        "status": "healthy",
        "phase": "2",
        "message": "Database integrated successfully",
        "stocks_count": stock_count,
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "next_phase": "Stock price data integration"
    })

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
        
        return jsonify({
            'success': True,
            'message': f'Stock {symbol} added successfully!',
            'stock': new_stock.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/phase3-prepare')
def phase3_prepare():
    return jsonify({
        "phase": "3",
        "status": "ready",
        "instructions": "Add data processing dependencies",
        "next_dependencies": ["pandas", "numpy", "yfinance"],
        "note": "These are larger packages - deploy carefully"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
