from datetime import datetime
from flask import Blueprint, current_app, render_template, request, redirect, flash, url_for, get_flashed_messages, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from utils import get_market_status
from db.db_models import Portfolio, Stock, User, StockHistory, Transaction
from db.db import db
from routes.api_v1 import get_stocks
from transaction import buy_stock, check_user_balance, sell_stock, balance_transaction
from forms import LoginForm, RegisterForm, TransactionForm, BalanceForm

# Create a blueprint for web routes
web = Blueprint('web', __name__)

# HOME ROUTE
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

# LOGIN ROUTE
@web.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
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
    return render_template('login.html', form=form)

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
    form = RegisterForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name  = form.last_name.data
        username   = form.username.data
        email      = form.email.data
        password   = form.password.data

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "danger")
        else:
            # Create a new user
            new_user = User(first_name=first_name, last_name=last_name, username=username, email=email)
            new_user.set_password(password) # Hash the password
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('web.login'))

    return render_template('register.html', form=form)

# TRANSACTION ROUTE (buy/sell)
@web.route("/transaction", methods=["POST"])
@login_required
def transaction():
    form = TransactionForm()

    if form.validate_on_submit():
        stock_id = form.stock_id.data
        quantity = form.quantity.data
        stock_symbol = form.stock_symbol.data
        stock = Stock.query.get(stock_id)


        if not stock:
            return jsonify({"status": "error", "message": "Stock not found."})
        
        action = request.form.get("action")
        if action == "buy":
            try:
                quantity = int(quantity)  # Ensure quantity is an integer
                result = buy_stock(current_user.id, stock_id, stock_symbol, quantity)
            except ValueError:
                return jsonify({"status": "error", "message": "Invalid quantity."})
        elif action == "sell":
            # Sell stock
            result = sell_stock(current_user.id, stock_id, stock_symbol, quantity)
        else:
            return jsonify({"status": "error", "message": "Invalid action."})
        
        if result["status"] == "success":
            return jsonify({"status": "success", "details": result["details"]})
        else:
            return jsonify({"status": "error", "message": result["message"]})
    
    return jsonify({"status": "error", "message": "Invalid form data."})

# PORTFOLIO ROUTE
@web.route("/portfolio")
@login_required
def portfolio():
    user_id = current_user.id
    balance = check_user_balance(user_id)
    with current_app.app_context():
        market_status = get_market_status(current_app)

    # Query the user's portfolio and join with the stock table to get stock details
    portfolio_data = db.session.query(Portfolio, Stock).filter(Portfolio.user == user_id).join(Stock, Portfolio.stock == Stock.id).all()

    # Render the portfolio template with the portfolio data
    portfolio = [
        {
            "id": entry.Stock.id,
            "symbol": entry.Stock.symbol,
            "name": entry.Stock.company,
            "shares": entry.Portfolio.quantity,
            "price": entry.Stock.price,
            "history": [
                {
                    "timestamp": history.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "price": history.price
                }
                for history in StockHistory.query.filter_by(stock_id=entry.Stock.id).order_by(StockHistory.timestamp).all()
            ]            
        }
        for entry in portfolio_data
    ] if portfolio_data else []

    # Query all stocks for buying
    all_stock_data = Stock.query.all()
    all_stocks = [
        {
            "id": stock.id,
            "symbol": stock.symbol,
            "company": stock.company,
            "quantity": stock.quantity,
            "price": stock.price,
            "history": [
                {
                    "timestamp": history.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "price": history.price
                }
                for history in StockHistory.query.filter_by(stock_id=stock.id).order_by(StockHistory.timestamp).all()
            ]
        }
        for stock in all_stock_data
    ] if all_stock_data else []

    # Paginate transactions table
    page = request.args.get('page', 1, type=int)
    per_page = current_user.pagination # Use the user's pagination setting

    # Alias the Stock table for clarity
    StockAlias = aliased(Stock)

    transactions_paginated = (
        db.session.query(Transaction, StockAlias.symbol.label('stock_symbol'))
        .join(StockAlias, Transaction.stock == StockAlias.id, isouter=True) # Left join (include transactions without stock)
        .filter(Transaction.user == user_id)
        .order_by(desc(Transaction.timestamp))
        .paginate(page=page, per_page=per_page)
    )
    form = TransactionForm()

    return render_template(
        'portfolio.html',
        portfolio=portfolio,
        all_stocks=all_stocks,
        form=form,
        transactions=transactions_paginated.items,
        pagination=transactions_paginated,
        balance=balance,
        market_status=market_status)

# BALANCE UPDATE ROUTE
@web.route('/update_balance', methods=['POST'])
@login_required
def update_balance():
    action = request.form.get("action")
    amount = request.form.get("amount", type=float)

    if action not in ['deposit', 'withdraw'] or not amount or amount <= 0:
        return jsonify({"status": "error", "message": "Invalid action or amount."}), 400

    result = balance_transaction(current_user.id, action, amount)
    
    if result["status"] == "success":
        return jsonify({"status": "success", "details": result["details"]})
    else:
        return jsonify({"status": "error", "message": result["message"]})
