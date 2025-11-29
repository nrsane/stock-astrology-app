import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from models.stock_models import db, StockPrice

class StockDataManager:
    def __init__(self):
        pass
    
    def fetch_stock_data(self, symbol, period="2y"):
        """Fetch stock data from Yahoo Finance"""
        try:
            yf_symbol = f"{symbol}.NS"
            stock = yf.Ticker(yf_symbol)
            hist_data = stock.history(period=period)
            return hist_data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def store_stock_prices(self, stock_id, hist_data):
        """Store historical prices in database"""
        try:
            for date, row in hist_data.iterrows():
                existing = StockPrice.query.filter_by(
                    stock_id=stock_id, 
                    time=date
                ).first()
                
                if not existing and not pd.isna(row['Close']):
                    stock_price = StockPrice(
                        stock_id=stock_id,
                        time=date,
                        open=float(row['Open']) if not pd.isna(row['Open']) else 0,
                        high=float(row['High']) if not pd.isna(row['High']) else 0,
                        low=float(row['Low']) if not pd.isna(row['Low']) else 0,
                        close=float(row['Close']) if not pd.isna(row['Close']) else 0,
                        volume=int(row['Volume']) if pd.notna(row['Volume']) else 0
                    )
                    db.session.add(stock_price)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error storing prices: {e}")
            return False
    
    def get_price_correlation_data(self, stock_id, start_date, end_date):
        """Get price data for correlation analysis"""
        try:
            prices = StockPrice.query.filter(
                StockPrice.stock_id == stock_id,
                StockPrice.time >= start_date,
                StockPrice.time <= end_date
            ).order_by(StockPrice.time).all()
            
            price_data = []
            for price in prices:
                price_data.append({
                    'time': price.time,
                    'close': price.close,
                    'volume': price.volume
                })
            
            return price_data
        except Exception as e:
            print(f"Error getting price data: {e}")
            return []
