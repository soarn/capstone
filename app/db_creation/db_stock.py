from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# TODO: #6 Create a Stock model
class Stock(db.Model):
    stock_id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    available_price = db.Column(db.Float, nullable=False)