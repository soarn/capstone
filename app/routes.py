# TODO: #1 Implement routes

from flask import Blueprint, render_template, request, jsonify, redirect, url_for

# Create a blueprint object
main = Blueprint('main', __name__, template_folder='templates')

# Route to Home Page
@main.route("/")
def home():
    return render_template('home.html')

@main.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

@main.route("/buy")
def buy():
    return render_template('buy.html')

@main.route("/sell")
def sell():
    return render_template('sell.html')