from flask import Flask, jsonify, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
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

# Stock Data Manager
class StockDataManager:
    def __init__(self):
        self.data_available = False
        try:
            import yfinance as yf
            import pandas as pd
            self.yf = yf
            self.pd = pd
            self.data_available = True
            print("✅ yfinance and pandas imported successfully!")
        except ImportError as e:
            print(f"❌ Data dependencies not available: {e}")

    def fetch_stock_data(self, symbol, period="1mo"):
        """Fetch stock data from Yahoo Finance"""
        if not self.data_available:
            return None
            
        try:
            yf_symbol = f"{symbol}.NS"
            stock = self.yf.Ticker(yf_symbol)
            hist_data = stock.history(period=period)
            
            if hist_data.empty:
                print(f"No data found for {symbol}")
                return None
                
            return hist_data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def store_stock_prices(self, stock_id, hist_data):
        """Store historical prices in database"""
        if not self.data_available:
            return False
            
        try:
            for date, row in hist_data.iterrows():
                # Check if record already exists
                existing = StockPrice.query.filter_by(
                    stock_id=stock_id, 
                    date=date.date()
                ).first()
                
                if not existing and not self.pd.isna(row['Close']):
                    stock_price = StockPrice(
                        stock_id=stock_id,
                        date=date.date(),
                        open_price=float(row['Open']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        close_price=float(row['Close']),
                        volume=int(row['Volume']) if self.pd.notna(row['Volume']) else 0
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
        .btn-warning { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
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
        .tab-container { margin: 20px 0; }
        .tab-buttons {
            display: flex;
            margin-bottom: 1rem;
            border-bottom: 2px solid #e1e5e9;
        }
        .tab-button {
            padding: 1rem 2rem;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 600;
            color: #666;
            border-bottom: 3px solid transparent;
        }
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
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
        @media (max-width: 768px) { 
            .grid { grid-template-columns: 1fr; } 
            .tab-buttons { flex-direction: column; }
            .price-item { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Stock Astrology App</h1>
        
        <div class="phase completed">
            <h2>✅ PHASE 3: REAL STOCK PRICE DATA</h2>
            <p><strong>Live NSE Stock Prices Integrated!</strong></p>
            <p>Data Source: Yahoo Finance | Database: SQLite | Price Records: <span id="priceRecords">0</span></p>
        </div>

        <div class="grid">
            <!-- Add Stock Form -->
            <div class="phase">
                <h3>📊 Add New Stock</h3>
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
                    
                    <button type="submit">Add Stock & Fetch Prices</button>
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
            
            <div class="tab-container">
                <div class="tab-buttons">
                    <button class="tab-button active" onclick="switchTab('prices-tab')">Price Data</button>
                    <button class="tab-button" onclick="switchTab('fetch-tab')">Fetch Prices</button>
                    <button class="tab-button" onclick="switchTab('stats-tab')">Statistics</button>
                </div>
                
                <!-- Prices Tab -->
                <div id="prices-tab" class="tab-content active">
                    <div class="price-data">
                        <div class="price-item price-header">
                            <div>Date</div>
                            <div>Open</div>
                            <div>High</div>
                            <div>Low</div>
                            <div>Close</div>
                        </div>
                        <div id="priceList">Select a stock and fetch prices to see data</div>
                    </div>
                </div>
                
                <!-- Fetch Tab -->
                <div id="fetch-tab" class="tab-content">
                    <div style="margin-bottom: 1rem;">
                        <label>Fetch Period:</label>
                        <select id="fetchPeriod">
                            <option value="1mo">1 Month</option>
                            <option value="3mo">3 Months</option>
                            <option value="6mo">6 Months</option>
                            <option value="1y">1 Year</option>
                        </select>
                    </div>
                    <button onclick="fetchStockPrices(currentStock)" class="btn-success">Fetch Latest Prices</button>
                    <div id="fetchResult" class="result" style="display: none; margin-top: 1rem;"></div>
                </div>
                
                <!-- Stats Tab -->
                <div id="stats-tab" class="tab-content">
                    <div id="stockStats">
                        <div class="result">Fetch price data to see statistics</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="phase">
            <h3>📈 Deployment Progress</h3>
            <p><strong>Phase 1:</strong> ✅ Basic Flask App</p>
            <p><strong>Phase 2:</strong> ✅ Database + Stock Management</p>
            <p><strong>Phase 3:</strong> ✅ Real Stock Price Data (Current)</p>
            <p><strong>Phase 4:</strong> ➡️ KP Astrology Features</p>
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

        // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

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
            resultDiv.innerHTML = 'Adding stock and fetching prices...';
            
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
                        <p>Now fetching current price data...</p>
                    `;
                    
                    // Auto-fetch prices for new stock
                    setTimeout(() => fetchStockPrices(symbol), 1000);
                    
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
        async function selectStock(symbol) {
            currentStock = symbol;
            
            // Update UI
            document.querySelectorAll('.stock-item').forEach(item => item.classList.remove('active'));
            document.getElementById(`stock-${symbol}`).classList.add('active');
            
            document.getElementById('stockAnalysis').style.display = 'block';
            document.getElementById('analysisTitle').textContent = `${symbol} - Price Analysis`;
            
            // Load price data
            loadStockPrices(symbol);
            switchTab('prices-tab');
        }

        // Load stock prices
        async function loadStockPrices(symbol) {
            try {
                const response = await fetch(`/api/stocks/${symbol}/prices?days=30`);
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
                    
                    updateStatistics(data.prices);
                } else {
                    priceList.innerHTML = '<div class="result warning">No price data available. Fetch prices first.</div>';
                }
            } catch (error) {
                document.getElementById('priceList').innerHTML = '<div class="result error">Error loading prices</div>';
            }
        }

        // Fetch stock prices
        async function fetchStockPrices(symbol) {
            if (!symbol) {
                alert('Please select a stock first');
                return;
            }
            
            const period = document.getElementById('fetchPeriod').value;
            const resultDiv = document.getElementById('fetchResult');
            resultDiv.style.display = 'block';
            resultDiv.className = 'result';
            resultDiv.innerHTML = `Fetching ${period} of price data for ${symbol}...`;
            
            try {
                const response = await fetch(`/api/stocks/${symbol}/fetch-prices`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ period: period })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <h4>✅ ${data.message}</h4>
                        <p><strong>Records Fetched:</strong> ${data.records_fetched}</p>
                        <p><strong>Period:</strong> ${data.period}</p>
                    `;
                    
                    // Reload price data
                    loadStockPrices(symbol);
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

        // Update statistics
        function updateStatistics(prices) {
            if (!prices || prices.length === 0) return;
            
            const latest = prices[prices.length - 1];
            const first = prices[0];
            const change = ((latest.close - first.close) / first.close) * 100;
            
            document.getElementById('stockStats').innerHTML = `
                <div class="grid">
                    <div class="result success">
                        <h4>Current Price</h4>
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
        "message": "Real Stock Price Data Integrated",
        "database": "sqlite",
        "data_available": stock_data_manager.data_available,
        "stocks_count": stock_count,
        "price_records": price_count,
        "timestamp": datetime.utcnow().isoformat(),
        "next_phase": "KP Astrology Features"
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

@app.route('/api/stocks/<symbol>/fetch-prices', methods=['POST'])
def fetch_stock_prices(symbol):
    """Fetch and store current stock prices"""
    try:
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
        
        data = request.get_json()
        period = data.get('period', '1mo')
        
        if not stock_data_manager.data_available:
            return jsonify({
                'success': False, 
                'error': 'Data processing dependencies not available'
            }), 500
        
        # Fetch data from Yahoo Finance
        hist_data = stock_data_manager.fetch_stock_data(symbol, period=period)
        
        if hist_data is None:
            return jsonify({'success': False, 'error': 'Failed to fetch stock data'}), 500
        
        # Store in database
        success = stock_data_manager.store_stock_prices(stock.id, hist_data)
        
        if success:
            price_count = StockPrice.query.filter_by(stock_id=stock.id).count()
            return jsonify({
                'success': True,
                'message': f'Stock prices fetched and stored for {symbol}',
                'records_fetched': len(hist_data),
                'price_records': price_count,
                'period': period
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

@app.route('/api/ready-for-phase4')
def ready_for_phase4():
    return jsonify({
        "phase": "4",
        "status": "ready",
        "instructions": "Add KP Astrology features",
        "features": [
            "Birth chart calculations",
            "House significators", 
            "Planetary positions",
            "Correlation analysis",
            "Price predictions"
        ],
        "note": "Final phase - complete astrology integration"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
