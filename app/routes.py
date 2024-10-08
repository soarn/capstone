# Place flask routes here

# TODO: #1 Implement routes

#Route to Home Page
from flask import Flask, render_template, request, jsonify
import routes

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

@app.route("/buy")
def buy():
    return render_template('buy.html')