from flask import Blueprint, render_template

# Create a blueprint for web routes
web = Blueprint('web', __name__)

# Route to Home Page
@web.route("/")
def home():
    return render_template('home.html')

@web.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

@web.route("/buy")
def buy():
    return render_template('buy.html')

@web.route("/sell")
def sell():
    return render_template('sell.html')

@web.route("/profile")
def profile():
    return render_template('profile.html')
