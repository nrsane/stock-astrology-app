from flask import Flask, jsonify, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
import requests
import json

app = Flask(__name__)

# Database configuration - SQLite only for now
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
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

# Stock Price Model
class StockPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
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

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

# Simple Stock Data Manager (No heavy dependencies)
class SimpleStockDataManager:
    def __init__(self):
        print("✅ Simple stock data manager initialized")
    
    def get_sample_price_data(self, symbol, days=30):
        """Generate sample price data (will replace with real API later)"""
        import random
        from datetime import datetime, timedelta
        
        base_price = random.uniform(100, 5000)
        prices = []
        
        for i in range(days):
            date = datetime.now().date() - timedelta(days=days - i - 1)
            price_change = random.uniform(-0.05, 0.05)
            close_price = base_price * (1 + price_change)
            
            prices.append({
                'date': date,
                'open': close_price * (1 + random.uniform(-0.02, 0.01)),
                'high': close_price * (1 + random.uniform(0, 0.03)),
                'low': close_price * (1 + random.uniform(-0.03, 0)),
                'close': close_price,
                'volume': random.randint(100000, 5000000)
            })
            
            base_price = close_price
        
        return prices

# Initialize stock data manager
stock_data_manager = SimpleStockDataManager()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Astrology App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
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
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .phase {
            background: #e3f2fd;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            border-left: 4px solid #2196f3;
        }
        .phase.completed {
            background: #d4edda;
            border-left-color: #28a745;
        }
        .phase.demo {
            background: #fff3cd;
            border-left-color: #ffc107;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, button, select { 
            width: 100%; 
            padding: 12px; 
            margin: 5px 0; 
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
        }
        input:focus, select:focus {
            border-color: #667eea;
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            cursor: pointer; 
            font-weight: 600;
        }
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-success { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .result { 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px;
        }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .warning { background: #fff3cd; color: #856404; }
        .stock-item { 
            padding: 15px; 
            border-bottom: 1px solid #eee; 
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .stock-item:hover { 
            background: #f8f9fa; 
            transform: translateX(5px);
        }
        .stock-item.active {
            background: #e3f2fd;
            border-left: 4px solid #667eea;
        }
        .price-data { 
            max-height: 400px; 
            overflow-y: auto; 
            margin: 10px 0;
        }
        .price-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
            gap: 10px;
        }
        .price-header {
            font-weight: bold;
            background: #f8f9fa;
        }
        .demo-note {
            background: #e7f3ff;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #2196f3;
        }
        @media (max-width: 768px) { 
            .grid { grid-template-columns: 1fr; } 
            .price-item { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Stock Astrology App</h1>
        
        <div class="phase completed">
            <h2>✅ PHASE 3: STOCK PRICE DATA (SIMPLIFIED)</h2>
            <p><strong>Stock Management with Demo Price Data Ready!</strong></p>
            <p>Database: SQLite | Stocks: <span id="stockCount">0</span> | Price Records: <span id="priceRecords">0</span></p>
        </div>

        <div class="phase demo">
            <h3>📊 Demo Mode Active</h3>
            <p><strong>Note:</strong> Using demo price data to avoid dependency issues.</p>
            <p>Real stock prices will be added in the next phase after we stabilize the deployment.</p>
        </div>

        <div class="grid">
            <!-- Add Stock Form -->
            <div class="phase">
                <h3>📈 Add New Stock</h3>
                <form onsubmit="addStock(event)">
                    <div class="form-group">
                        <label for="symbol">Stock Symbol (NSE):</label>
                        <input type="text" id="symbol" placeholder="e.g., RELIANCE, TCS, INFY" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="name">Company Name:</label>
                        <input type="text" id="name" placeholder="e.g., Reliance Industries Limited">
                    </div>
                    
                    <div class="form-group">
                        <label for="listingDate">Listing Date:</label>
                        <input type="date" id="listingDate" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="listingTime">Listing Time:</label>
                        <input type="time" id="listingTime" value="10:00">
                    </div>
                    
                    <button type="submit">Add Stock to Database</button>
                </form>
                <div id="formResult" class="result" style="display: none;"></div>
            </div>

            <!-- Stock List -->
            <div class="phase">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>📋 Stock Portfolio</h3>
                    <button onclick="loadStocks()" style="width: auto; padding: 8px 16px;">Refresh</button>
                </div>
                <div id="stockList" style="max-height: 400px; overflow-y: auto;">
                    <div class="result">Loading stocks...</div>
                </div>
            </div>
        </div>

        <!-- Selected Stock Analysis -->
        <div class="phase" id="stockAnalysis" style="display: none;">
            <h2 id="analysisTitle">Stock Analysis</h2>
            
            <div class="demo-note">
                <strong>Demo Data:</strong> Price data is simulated for demonstration. Real market data will be integrated in Phase 4.
            </div>
            
            <div style="margin-bottom: 1rem;">
                <button onclick="generateDemoPrices(currentStock)" class="btn-success">Generate Demo Price Data</button>
                <select id="demoDays" style="width: auto; margin-left: 1rem;">
                    <option value="7">7 Days</option>
                    <option value="30" selected>30 Days</option>
                    <option value="90">90 Days</option>
                </select>
            </div>
            
            <div class="price-data">
                <div class="price-item price-header">
                    <div>Date</div>
                    <div>Open</div>
                    <div>High</div>
                    <div>Low</div>
                    <div>Close</div>
                </div>
                <div id="priceList">Generate demo data to see price information</div>
            </div>
            
            <div id="priceStats" style="margin-top: 20px;"></div>
        </div>

        <div class="phase">
            <h3>📊 Deployment Progress</h3>
            <p><strong>Phase 1:</strong> ✅ Basic Flask App</p>
            <p><strong>Phase 2:</strong> ✅ Database + Stock Management</p>
            <p><strong>Phase 3:</strong> ✅ Stock Management + Demo Prices (Current)</p>
            <p><strong>Phase 4:</strong> ➡️ Real Stock Prices + KP Astrology</p>
        </div>

        <div style="margin-top: 30px; text-align: center;">
            <h3>🔧 Next Steps</h3>
            <p>After this phase stabilizes, we'll add:</p>
            <ul style="display: inline-block; text-align: left;">
                <li>Real NSE stock price integration</li>
                <li>KP Astrology birth charts</li>
                <li>House significator analysis</li>
                <li>Price correlation with planetary movements</li>
            </ul>
        </div>
    </div>

    <script>
        let currentStock = null;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('listingDate').valueAsDate = new Date();
            loadStocks();
            updateStats();
        });

        // Add stock
        async function addStock(e) {
            e.preventDefault();
            const symbol = document.getElementById('symbol').value.toUpperCase();
            const name = document.getElementById('name').value;
            const listingDate = document.getElementById('listingDate').value;
            const listingTime = document.getElementById('listingTime').value;
            
            const resultDiv = document.getElementById('formResult');
            resultDiv.style.display = 'block';
            resultDiv.className = 'result';
            resultDiv.innerHTML = 'Adding stock to database...';
            
            try {
                const response = await fetch('/api/stocks', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        symbol: symbol,
                        name: name,
                        listing_date: listingDate,
                        listing_time: listingTime
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <h4>✅ ${data.message}</h4>
                        <p><strong>Symbol:</strong> ${data.stock.symbol}</p>
                        <p><strong>Name:</strong> ${data.stock.name}</p>
                        <p><strong>Listing:</strong> ${data.stock.listing_date} at ${data.stock.listing_time}</p>
                    `;
                    
                    // Clear form and refresh
                    document.getElementById('symbol').value = '';
                    document.getElementById('name').value = '';
                    document.getElementById('listingDate').valueAsDate = new Date();
                    
                    loadStocks();
                    updateStats();
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<h4>❌ Error</h4><p>${data.error}</p>`;
                }
            } catch (error) {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `<h4>❌ Network Error</h4><p>${error.message}</p>`;
            }
        }

        // Load stocks
        async function loadStocks() {
            try {
                const stockList = document.getElementById('stockList');
                stockList.innerHTML = '<div class="result">Loading...</div>';
                
                const response = await fetch('/api/stocks');
                const data = await response.json();
                
                if (data.success && data.stocks.length > 0) {
                    stockList.innerHTML = data.stocks.map(stock => `
                        <div class="stock-item" onclick="selectStock('${stock.symbol}')" id="stock-${stock.symbol}">
                            <strong>${stock.symbol}</strong>
                            <div style="color: #666; font-size: 0.9rem; margin-top: 5px;">
                                ${stock.name}<br>
                                Listed: ${stock.listing_date}
                                <div style="color: #667eea; font-weight: 600;">Click to analyze</div>
                            </div>
                        </div>
                    `).join('');
                } else {
                    stockList.innerHTML = '<div class="result">No stocks found. Add your first stock!</div>';
                }
            } catch (error) {
                document.getElementById('stockList').innerHTML = '<div class="result error">Error loading stocks</div>';
            }
        }

        // Select stock
        function selectStock(symbol) {
            currentStock = symbol;
            
            // Update UI
            document.querySelectorAll('.stock-item').forEach(item => item.classList.remove('active'));
            document.getElementById(`stock-${symbol}`).classList.add('active');
            
            document.getElementById('stockAnalysis').style.display = 'block';
            document.getElementById('analysisTitle').textContent = `${symbol} - Price Analysis (Demo)`;
            
            // Clear previous data
            document.getElementById('priceList').innerHTML = 'Generate demo data to see price information';
            document.getElementById('priceStats').innerHTML = '';
        }

        // Generate demo prices
        async function generateDemoPrices(symbol) {
            if (!symbol) {
                alert('Please select a stock first');
                return;
            }
            
            const days = document.getElementById('demoDays').value;
            
            try {
                const response = await fetch(`/api/stocks/${symbol}/demo-prices`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ days: parseInt(days) })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    loadStockPrices(symbol);
                    updateStats();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Network error: ' + error.message);
            }
        }

        // Load stock prices
        async function loadStockPrices(symbol) {
            try {
                const response = await fetch(`/api/stocks/${symbol}/prices`);
                const data = await response.json();
                
                const priceList = document.getElementById('priceList');
                if (data.success && data.prices.length > 0) {
                    priceList.innerHTML = data.prices.map(price => `
                        <div class="price-item">
                            <div>${price.date}</div>
                            <div>₹${price.open?.toFixed(2) || 'N/A'}</div>
                            <div>₹${price.high?.toFixed(2) || 'N/A'}</div>
                            <div>₹${price.low?.toFixed(2) || 'N/A'}</div>
                            <div>₹${price.close?.toFixed(2) || 'N/A'}</div>
                        </div>
                    `).join('');
                    
                    updatePriceStatistics(data.prices);
                } else {
                    priceList.innerHTML = '<div class="result warning">No price data available. Generate demo data first.</div>';
                }
            } catch (error) {
                document.getElementById('priceList').innerHTML = '<div class="result error">Error loading prices</div>';
            }
        }

        // Update price statistics
        function updatePriceStatistics(prices) {
            if (!prices || prices.length === 0) return;
            
            const latest = prices[prices.length - 1];
            const first = prices[0];
            const change = ((latest.close - first.close) / first.close) * 100;
            
            document.getElementById('priceStats').innerHTML = `
                <div class="grid">
                    <div class="result success">
                        <h4>Current Price (Demo)</h4>
                        <p style="font-size: 1.5rem; font-weight: bold;">₹${latest.close.toFixed(2)}</p>
                        <p>${latest.date}</p>
                    </div>
                    <div class="result ${change >= 0 ? 'success' : 'error'}">
                        <h4>Period Change</h4>
                        <p style="font-size: 1.5rem; font-weight: bold;">${change >= 0 ? '+' : ''}${change.toFixed(2)}%</p>
                        <p>${prices.length} trading days</p>
                    </div>
                </div>
            `;
        }

        // Update stats
        async function updateStats() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                document.getElementById('stockCount').textContent = data.stocks_count || 0;
                document.getElementById('priceRecords').textContent = data.price_records || 0;
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health')
def health_check():
    stock_count = Stock.query.count()
    price_count = StockPrice.query.count()
    return jsonify({
        "status": "healthy",
        "phase": "3",
        "message": "Stock Management with Demo Prices",
        "database": "sqlite",
        "stocks_count": stock_count,
        "price_records": price_count,
        "timestamp": datetime.utcnow().isoformat(),
        "next_phase": "Real stock prices + KP Astrology"
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

@app.route('/api/stocks/<symbol>/demo-prices', methods=['POST'])
def generate_demo_prices(symbol):
    """Generate demo price data"""
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        data = request.get_json()
        days = data.get('days', 30)
        
        # Generate demo data
        demo_prices = stock_data_manager.get_sample_price_data(symbol, days)
        
        # Store in database
        for price_data in demo_prices:
            existing = StockPrice.query.filter_by(
                stock_id=stock.id, 
                date=price_data['date']
            ).first()
            
            if not existing:
                stock_price = StockPrice(
                    stock_id=stock.id,
                    date=price_data['date'],
                    open_price=price_data['open'],
                    high_price=price_data['high'],
                    low_price=price_data['low'],
                    close_price=price_data['close'],
                    volume=price_data['volume']
                )
                db.session.add(stock_price)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Demo price data generated for {symbol}',
            'records_generated': len(demo_prices),
            'period': f'{days} days'
        })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/<symbol>/prices', methods=['GET'])
def get_stock_prices(symbol):
    """Get stock price data"""
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        prices = StockPrice.query.filter_by(stock_id=stock.id).order_by(StockPrice.date.desc()).limit(30).all()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'prices': [price.to_dict() for price in prices],
            'count': len(prices),
            'note': 'Demo data - real prices coming in Phase 4'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ready-for-phase4')
def ready_for_phase4():
    return jsonify({
        "phase": "4",
        "status": "ready",
        "instructions": "Add KP Astrology features with real stock prices",
        "note": "Current deployment is stable. Next phase will add astrology calculations."
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
