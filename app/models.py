from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class InvestmentOpportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(100), nullable=False)  # e.g., "NSE", "CBK"
    url = db.Column(db.String(500), nullable=False)
    country = db.Column(db.String(50), default="Kenya")
    type = db.Column(db.String(50))  # bond, ipo, share_offer
    published_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    requests_used = db.Column(db.Integer, default=0)
    request_limit = db.Column(db.Integer, default=1000)  # monthly
    created_at = db.Column(db.DateTime, default=datetime.utcnow)