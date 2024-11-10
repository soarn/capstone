from db.db import db
from datetime import datetime, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import uuid

# Create User Model (User)
class User(UserMixin, db.Model):
    # UserMixin provides default implementations for the methods required by Flask-Login
    id               = db.Column(db.Integer, primary_key=True)
    username         = db.Column(db.String(80), nullable=False, unique=True)
    password_hash    = db.Column(db.String(200), nullable=False)
    email            = db.Column(db.String(120), nullable=False, unique=True)
    verified         = db.Column(db.Boolean, nullable=False, default=False)
    created_at       = db.Column(db.DateTime, nullable=False, default=datetime.now())
    last_login       = db.Column(db.DateTime, nullable=True)
    role             = db.Column(db.String(50), nullable=False, default='user')
    status           = db.Column(db.String(20), nullable=False, default='active')
    balance          = db.Column(db.Float, nullable=False, default=0.0)
    notifications    = db.Column(db.Boolean, nullable=False, default=True)
    theme            = db.Column(db.String(20), default="default")
    data_sharing     = db.Column(db.Boolean, default=True)
    confetti_enabled = db.Column(db.Boolean, nullable=False, default=True)
    pagination       = db.Column(db.Integer, nullable=False, default=10)
    first_name       = db.Column(db.String(50), nullable=False, default=username)
    last_name        = db.Column(db.String(50), nullable=False, default=username)

    # Hash the password before storing it
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check the password against the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create Portfolio Model (Portfolio)
class Portfolio(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    user     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock    = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price    = db.Column(db.Float, nullable=False)

# Create Stock Model (Stock)
class Stock(db.Model):
    id                     = db.Column(db.Integer, primary_key=True)
    symbol                 = db.Column(db.String(10), unique=True, nullable=False)
    company                = db.Column(db.String(128), nullable=False)
    price                  = db.Column(db.Numeric(10,2), nullable=False)            # Current Price
    quantity               = db.Column(db.Integer, nullable=False)                  # Available stock quantity
    manual_price           = db.Column(db.Numeric(10,2), nullable=True)             # Admin-controlled price
    is_manual              = db.Column(db.Boolean, nullable=False, default=False)   # Whether the price is manually set
    fluctuation_multiplier = db.Column(db.Float, default=1.0)                       # Multiplier for good/bad days

# Create StockHistory Model (StockHistory)
class StockHistory(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    stock_id  = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    price     = db.Column(db.Numeric(10,2), nullable=False)
    quantity  = db.Column(db.Integer, nullable=False)

# Create Transaction Model (Transaction)

class Transaction(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock     = db.Column(db.Integer, db.ForeignKey('stock.id'))
    type      = db.Column(db.String(10), nullable=False)
    quantity  = db.Column(db.Integer, nullable=False)
    price     = db.Column(db.Numeric(10,2))
    amount    = db.Column(db.Numeric(10,2), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    # Marker Fields
    marker_flag = db.Column(db.Boolean, default=False) # True if the transaction is a marker transaction
    marker_text = db.Column(db.String(254), nullable=True) # (Optional) Text for the marker transaction

# Create Admin Model for Market Hours (Admin)
class AdminSettings(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    market_open = db.Column(db.Time, default=time(8, 0)) 
    market_close = db.Column(db.Time, default=time(16, 0))
    open_days = db.Column(db.String(254), default="Monday,Tuesday,Wednesday,Thursday,Friday")  # Comma-separated days because MySQL doesn't support ARRAY :(
    close_on_holidays = db.Column(db.Boolean, default=True)

    # Convert open_days to a list for easier handling
    @property
    def open_days_list(self):
        return self.open_days.split(',') if self.open_days else []

    @open_days_list.setter
    def open_days_list(self, days):
        self.open_days = ','.join(days) if days else ""
    @property
    
    # Add property methods for safe conversions
    def market_open_time(self):
        if isinstance(self.market_open, str):
            return datetime.strptime(self.market_open, '%H:%M').time()
        return self.market_open

    @property
    def market_close_time(self):
        if isinstance(self.market_close, str):
            return datetime.strptime(self.market_close, '%H:%M').time()
        return self.market_close
    
# Create Database Tables
# @app.route("/")
# def index():
#     db.create_all()
#     return "Database tables created!"