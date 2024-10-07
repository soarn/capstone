
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

db = SQLAlchemy()

db.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")
db.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# TODO: #4 Create a User model
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)