from datetime import datetime
from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages
from flask_login import login_user, logout_user, login_required
from db.db_models import Stock, User, Portfolio, Transaction
from db.db import db

buy_blueprint = Blueprint('buy', __name__)


def buy_stock(user_id, stock_symbol, quantity):
    # Fetch the user from the database
    user = User.query.get(user_id)
    if not user:
        return {"status": "error", "message": "User not found."}

    # Find the stock by symbol
    stock = Stock.query.filter_by(symbol=stock_symbol).first()
    if not stock:
        return {"status": "error", "message": "Stock not found."}

    # Check if there is enough stock available
    if stock.quantity < quantity:
        return {"status": "error", "message": "Not enough stock available."}

    # Calculate total price of the purchase
    total_price = stock.price * quantity

    # Check if the user has enough balance
    if user.balance < total_price:
        return {"status": "error", "message": "Insufficient balance."}

    # Deduct the user's balance
    user.balance -= total_price

    # Deduct the quantity from available stock
    stock.quantity -= quantity

    # Check if the user already has this stock in their portfolio
    portfolio_item = Portfolio.query.filter_by(user=user.id, stock=stock.id).first()

    if portfolio_item:
        # Update the quantity of the stock in the user's portfolio
        portfolio_item.quantity += quantity
    else:
        # Create a new portfolio item for this stock
        new_portfolio_item = Portfolio(
            user=user.id,
            stock=stock.id,
            quantity=quantity,
            price=stock.price
        )
        db.session.add(new_portfolio_item)

    # Create a new transaction record for the purchase
    new_transaction = Transaction(
        user=user.id,
        stock=stock.id,
        type="buy",
        quantity=quantity,
        price=stock.price,
        amount=total_price,
        timestamp=datetime.now()
    )
    db.session.add(new_transaction)

    # Commit all changes to the database
    db.session.commit()

    return {"status": "success", "message": f"Successfully purchased {quantity} shares of {stock.company}."}

# Fetch available stocks for the buy page
def all_stocks():
    return Stock.query.all()

# Get user balance
def check_user_balance(user_id):
    user = User.query.get(user_id)
    if user:
        return user.balance
    return 0

@buy_blueprint.route("/buy", methods=["GET", "POST"])
@login_required
def buy_page():
    if request.method == "POST":
        # Get the stock symbol and quantity from the form
        stock_symbol = request.form.get("stock.symbol")
        quantity = int(request.form.get("quantity"))

        # Call the buy_stock function to handle the purchase
        result = buy_stock(id, stock_symbol, quantity)

        if result["status"] == "error":
            flash(result["message"], "danger")
        else:
            flash(result["message"], "success")

        return redirect(url_for('buy.buy_page'))

    # Get the list of available stocks
    stocks = all_stocks()
    

    return render_template('buy.html', stocks=stocks)