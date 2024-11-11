from datetime import datetime
from utils import get_market_status
from flask import current_app, flash, redirect, request
from db.db_models import Stock, User, Portfolio, Transaction
from db.db import db
from sqlalchemy.exc import IntegrityError
import uuid

def buy_stock(user_id, stock_id, stock_symbol, quantity):
    # Fetch the user from the database
    user = User.query.get(user_id)
    if not user:
        return {"status": "error", "message": "User not found."}
    
    # Check if the market is open
    with current_app.app_context():
        market_status = get_market_status(current_app)
    
    if market_status != "open":
        return {"status": "error", "message": "Market is closed."}

    # Find the stock by symbol
    stock = Stock.query.filter_by(id=stock_id).first()
    if not stock:
        return {"status": "error", "message": "Stock not found."}

    # Check if there is enough stock available
    if stock.quantity < quantity:
        return {"status": "error", "message": "Insufficient stock available."}

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
    portfolio_entry = Portfolio.query.filter_by(user=user_id, stock=stock_id).first()
    if not portfolio_entry:
        portfolio_entry = Portfolio(user=user_id, stock=stock_id, quantity=0, price=stock.price)
        db.session.add(portfolio_entry)
    
    portfolio_entry.quantity += quantity

    # Create a new transaction record for the purchase
    order_number = str(uuid.uuid4())
    new_transaction = Transaction(
        user=user.id,
        stock=stock.id,
        type="buy",
        quantity=quantity,
        price=stock.price,
        amount=total_price, 
        order_number=order_number,
        timestamp=datetime.now(),
        timestamp_unix=int(datetime.now().timestamp())
    )
    db.session.add(new_transaction)

    # Commit all changes to the database
    db.session.commit()

    return {
        "status": "success", 
        "message": f"Successfully sold {quantity} shares of {stock_symbol}.",
        "details": {
            "order_number": order_number,
            "symbol": stock_symbol,
            "company": stock.company,
            "quantity": quantity,
            "price": stock.price,
            "total_price": total_price
        }
    }

# Fetch available stocks for the buy page
def all_stocks():
    return Stock.query.all()

# Get user balance
def check_user_balance(user_id):
    user = User.query.get(user_id)
    if user:
        return user.balance
    return 0

# Update user portfolio
def update_portfolio(user_id, stock_id, quantity, purchase_price):
    # Check if the user already has this stock in their portfolio
    portfolio_entry = Portfolio.query.filter_by(user=user_id, stock=stock_id).first()

    if portfolio_entry:
        # Update the quantity and the price
        portfolio_entry.quantity += quantity
        # Update the price to the latest purchase price
        portfolio_entry.price = purchase_price
    else:
        # Create a new portfolio entry
        new_portfolio_entry = Portfolio(
            user=user_id,
            stock=stock_id,
            quantity=quantity,
            price=purchase_price
        )
        db.session.add(new_portfolio_entry)

    db.session.commit()

# Sell stock
def sell_stock(user_id, stock_id, stock_symbol, quantity):
    # Fetch the user from the database
    user = User.query.get(user_id)
    if not user:
        return {"status": "error", "message": "User not found."}
    
    # Check if the market is open
    with current_app.app_context():
        market_status = get_market_status(current_app)
    
    if market_status != "open":
        return {"status": "error", "message": "Market is closed."}

    # Find the stock by ID
    stock = Stock.query.filter_by(id=stock_id).first()
    if not stock:
        return {"status": "error", "message": "Stock not found."}

    # Check if the user has the stock in their portfolio
    portfolio_entry = Portfolio.query.filter_by(user=user_id, stock=stock_id).first()
    if not portfolio_entry or portfolio_entry.quantity < quantity:
        return {"status": "error", "message": "Insufficient shares to sell."}

    # Calculate the total sale price
    total_sale_price = stock.price * quantity

    # Increase user's balance with the sale amount
    user.balance += total_sale_price

    # Increase the stock's available quantity
    stock.quantity += quantity

    # Update the portfolio by subtracting the sold quantity
    portfolio_entry.quantity -= quantity

    # If the quantity reaches zero, remove the portfolio entry
    if portfolio_entry.quantity == 0:
        db.session.delete(portfolio_entry)

    # Log the transaction as a 'sell' operation
    order_number = str(uuid.uuid4())
    new_transaction = Transaction(
        user=user.id,
        stock=stock.id,
        type="sell",
        quantity=quantity,
        price=stock.price,
        amount=total_sale_price,
        order_number=order_number,
        timestamp=datetime.now(),
        timestamp_unix=int(datetime.now().timestamp())
    )
    db.session.add(new_transaction)
    # Commit all changes to the database
    db.session.commit()

    return {
        "status": "success", 
        "message": f"Successfully sold {quantity} shares of {stock_symbol}.",
        "details": {
            "order_number": order_number,
            "symbol": stock_symbol,
            "company": stock.company,
            "quantity": quantity,
            "price": stock.price,
            "total_price": total_sale_price
        }
    }

# Update User Balance
def balance_transaction (user_id, action, amount):

    # Fetch the user from the database
    user = User.query.get(user_id)
    if not user:
        return {"status": "error", "message": "User not found."}
    
    print(f"Initial balance: {user.balance}")

    if action == 'deposit':
        user.balance += amount
    elif action == 'withdraw':
        if user.balance < amount:
            return {"status": "error", "message": "Insufficient funds."}
        user.balance -= amount
    
    # Create a new transaction record for the balance update
    order_number = str(uuid.uuid4())
    new_transaction = Transaction(
        user=user.id,
        stock=None,  # Balance transactions may not have a stock ID
        type=action,
        quantity=0,  # Set quantity to 0 for balance actions
        price=amount,
        amount=user.balance,
        order_number=order_number,
        timestamp=datetime.now(),
        timestamp_unix=int(datetime.now().timestamp())
    )

    # Debug transaction fields before adding to session
    print(f"Prepared transaction: {new_transaction.__dict__}")

    # Add transaction to session and commit
    try:
        db.session.add(new_transaction)
        db.session.commit()
        print("Transaction committed successfully.")
        
        # Confirm transaction exists in database
        saved_transaction = Transaction.query.filter_by(order_number=order_number).first()
        if saved_transaction:
            print("Transaction saved successfully:", saved_transaction.__dict__)
        else:
            print("Transaction not found in database after commit.")
        
        return {
            "status": "success",
            "details": {
                "order_number": order_number,
                "action": action,
                "amount": amount,
                "new_balance": user.balance
            }
        }
    except IntegrityError as e:
        db.session.rollback()
        print(f"IntegrityError: {e}")
        return {"status": "error", "message": f"Integrity error: {e}"}
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")
        return {"status": "error", "message": f"Exception occurred: {e}"}