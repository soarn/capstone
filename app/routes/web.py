from datetime import datetime
from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages
from flask_login import login_user, logout_user, login_required
from db.db_models import Stock, User
from db.db import db
from routes.api_v1 import get_stocks

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
@login_required
def portfolio():
    return render_template('portfolio.html')

@web.route('/buy', methods=['GET', 'POST'])
def buy():
    stocks = get_stocks()  # Fetch stocks from the API or another app
    if request.method == 'POST':
        stock_symbol = request.form.get('stock')
        quantity = int(request.form.get('quantity'))

        # Find the stock by symbol
        stock = next((item for item in stocks if item["symbol"] == stock_symbol), None)

        if stock:
            total_cost = stock['price'] * quantity

            if portfolio['cash'] >= total_cost:
                portfolio['cash'] -= total_cost
                portfolio['stocks'][stock_symbol] = portfolio['stocks'].get(stock_symbol, 0) + quantity
                flash(f"Successfully purchased {quantity} shares of {stock['name']} for ${total_cost}", 'success')
            else:
                flash("Not enough cash to complete the purchase", 'danger')

        return redirect(url_for('buy'))

    # Calculate portfolio value including cash and stocks
    """ RAN INTO AN ERROR HERE """
    portfolio_value = sum(
        next((stock['price'] for stock in stocks if stock['symbol'] == stock_symbol), 0) * quantity
        for stock_symbol, quantity in portfolio['stocks'].items()
    ) + portfolio['cash']

    return render_template('buy.html', stocks=stocks, portfolio_value=portfolio_value)

@web.route("/sell")
@login_required
def sell():
    return render_template('sell.html')

# LOGIN ROUTE
@web.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Update the last login time
            user.last_login = datetime.now()
            db.session.commit()

            # Log the user in, remember me is optional
            login_user(user, remember=remember)

            # Clear any flashed messages
            get_flashed_messages()

            # Get the 'next' argument to see where the user was redirected from
            next_page = request.args.get('next')

            # Only flash if user was not redirected to login
            if not next_page:
                flash("Login successful!", "success")

            # Redirect to the next page if it exists, otherwise, redirect to profile by default
            if next_page:
                return redirect(next_page)
            return redirect(url_for('profile.profile_page'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
    return render_template('login.html')

# LOGOUT ROUTE
@web.route("/logout")
@login_required
def logout():
    # Log the user out
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('web.home'))

# REGISTER ROUTE
@web.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "danger")
        else:
            # Create a new user
            new_user = User(username=username, email=email)
            new_user.set_password(password) # Hash the password
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('web.login'))
    return render_template('register.html')