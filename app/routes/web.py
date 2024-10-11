from flask import Blueprint, render_template
from db.db_models import Stock, db

# Create a blueprint for web routes
web = Blueprint('web', __name__)

# Route to Home Page
@web.route("/")
def home():
    #defining whats popular
    popular_symbols = ['AAPL', 'AMZN', 'GOOG', 'TSLA', 'NVDA']
    #query the database for the popular stocks
    popular_stocks = Stock.query.filter(Stock.symbol.in_(popular_symbols)).all()
    # Query all stocks from the database
    all_stocks = Stock.query.all()

    # Pass the stocks to the template
    return render_template('home.html', popular_stocks=popular_stocks, all_stocks=all_stocks)
    

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
