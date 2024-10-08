from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Create User Model (User)
class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    verified      = db.Column(db.Boolean, default=False, nullable=False)
    created_at    = db.Column(db.DateTime, nullable=False)
    last_login    = db.Column(db.DateTime)
    role          = db.Column(db.String(50), nullable=False, default='user')
    status        = db.Column(db.String(20), nullable=False, default='active')
    balance       = db.Column(db.Float, nullable=False)

    # Hash the password before storing it
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check the password against the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create Account Settings (Account_Settings)
class AccountSettings(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    user          = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notifications = db.Column(db.Boolean, nullable=False)
    theme         = db.Column(db.Boolean, nullable=False)

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
@app.route("/")
def index():
    db.create_all()
    return "Database tables created!"