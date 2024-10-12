from db.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Create User Model (User)
class User(UserMixin, db.Model):
    # UserMixin provides default implementations for the methods required by Flask-Login
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    email         = db.Column(db.String(120), nullable=False, unique=True)
    verified      = db.Column(db.Boolean, nullable=False, default=False)
    created_at    = db.Column(db.DateTime, nullable=False, default=datetime.now())
    last_login    = db.Column(db.DateTime, nullable=True)
    role          = db.Column(db.String(50), nullable=False, default='user')
    status        = db.Column(db.String(20), nullable=False, default='active')
    balance       = db.Column(db.Float, nullable=False, default=0.0)
    notifications = db.Column(db.Boolean, nullable=False, default=True)
    theme               = db.Column(db.String(20), default="default")
    data_sharing        = db.Column(db.Boolean, default=True)

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
    id       = db.Column(db.Integer, primary_key=True)
    symbol   = db.Column(db.String(10), unique=True, nullable=False)
    company  = db.Column(db.String(100), nullable=False)
    price    = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)

# Create Transaction Model (Transaction)

class Transaction(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    user      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock     = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    type      = db.Column(db.String(10), nullable=False)
    quantity  = db.Column(db.Integer, nullable=False)
    price     = db.Column(db.Float, nullable=False)
    amount    = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
# Create Database Tables
# @app.route("/")
# def index():
#     db.create_all()
#     return "Database tables created!"