from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Stock(db.Model):
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200))
    listing_date = db.Column(db.Date, nullable=False)
    listing_time = db.Column(db.Time, nullable=False, default='10:00:00')
    exchange = db.Column(db.String(50), default='NSE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    birth_chart = db.relationship('BirthChart', backref='stock', uselist=False, cascade="all, delete-orphan")
    house_significators = db.relationship('HouseSignificator', backref='stock', cascade="all, delete-orphan")
    price_data = db.relationship('StockPrice', backref='stock', cascade="all, delete-orphan")

class BirthChart(db.Model):
    __tablename__ = 'birth_charts'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    ascendant_degree = db.Column(db.Float)
    cusps = db.Column(db.JSON)
    planet_positions = db.Column(db.JSON)
    house_positions = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HouseSignificator(db.Model):
    __tablename__ = 'house_significators'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    house_number = db.Column(db.Integer, nullable=False)
    cuspal_sign_lord = db.Column(db.String(20))
    cuspal_star_lord = db.Column(db.String(20))
    cuspal_sub_lord = db.Column(db.String(20))
    occupying_planets = db.Column(db.JSON)
    all_significators = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StockPrice(db.Model):
    __tablename__ = 'stock_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_stock_prices_time', 'time'),
        db.Index('idx_stock_prices_stock_id', 'stock_id'),
    )
