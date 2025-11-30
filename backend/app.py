from flask import Flask, jsonify, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

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

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Astrology App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
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
        input:focus {
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
        .result { 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px;
        }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .stock-item { 
            padding: 15px; 
            border-bottom: 1px solid #eee; 
            cursor: pointer;
        }
        .stock-item:hover { background: #f8f9fa; }
        @media (max-width: 768px) { 
            .grid { grid-template-columns: 1fr; } 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Stock Astrology App</h1>
        
        <div class="phase completed">
            <h2>✅ PHASE 2: DATABASE & STOCK MANAGEMENT</h2>
            <p><strong>SQLite Database + Stock Management Ready!</strong></p>
            <p>Database: SQLite | Stocks: <span id="stockCount">0</span></p>
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
                    
                    <button type="submit">Add Stock to Database</button>
                </form>
                <div id="formResult" class="result" style="display: none;"></div>
            </div>

            <!-- Stock List -->
            <div class="phase">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>📋 Existing Stocks</h3>
                    <button onclick="loadStocks()" style="width: auto; padding: 8px 16px;">Refresh</button>
                </div>
                <div id="stockList" style="max-height: 400px; overflow-y: auto;">
                    <div class="result">Loading stocks...</div>
                </div>
            </div>
        </div>

        <div class="phase">
            <h3>📈 Deployment Progress</h3>
            <p><strong>Phase 1:</strong> ✅ Basic Flask App</p>
            <p><strong>Phase 2:</strong> ✅ Database + Stock Management (Current)</p>
            <p><strong>Phase 3:</strong> ➡️ Real Stock Price Data</p>
            <p><strong>Phase 4:</strong> ➡️ KP Astrology Features</p>
        </div>

        <div style="margin-top: 30px; text-align: center;">
            <h3>🔧 API Endpoints</h3>
            <p><a href="/api/health" style="color: #667eea; margin: 0 10px;">Health Check</a></p>
            <p><a href="/api/stocks" style="color: #667eea; margin: 0 10px;">List Stocks (API)</a></p>
        </div>
    </div>

    <script>
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('listingDate').valueAsDate = new Date();
            loadStocks();
            updateStockCount();
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
            resultDiv.innerHTML = 'Adding stock...';
            
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
                    // Clear form
                    document.getElementById('symbol').value = '';
                    document.getElementById('name').value = '';
                    document.getElementById('listingDate').valueAsDate = new Date();
                    
                    // Refresh lists
                    loadStocks();
                    updateStockCount();
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
                        <div class="stock-item" onclick="viewStock('${stock.symbol}')">
                            <strong>${stock.symbol}</strong>
                            <div style="color: #666; font-size: 0.9rem; margin-top: 5px;">
                                ${stock.name}<br>
                                Listed: ${stock.listing_date} at ${stock.listing_time}
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

        // Update stock count
        async function updateStockCount() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                document.getElementById('stockCount').textContent = data.stocks_count || 0;
            } catch (error) {
                console.error('Error updating count:', error);
            }
        }

        // View stock details
        function viewStock(symbol) {
            alert(`Stock: ${symbol}\n\nDetails will be shown in Phase 3 with price data and KP analysis.`);
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
    return jsonify({
        "status": "healthy",
        "phase": "2",
        "message": "Database & Stock Management Ready",
        "database": "sqlite",
        "stocks_count": stock_count,
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

@app.route('/api/ready-for-phase3')
def ready_for_phase3():
    return jsonify({
        "phase": "3",
        "status": "ready",
        "instructions": "Add stock price data integration",
        "dependencies_needed": ["pandas", "numpy", "yfinance"],
        "note": "Will add real stock price data from NSE"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
