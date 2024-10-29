from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify
from flask_login import current_user, login_required
from functools import wraps
from db.db_models import Stock, User, Transaction
from db.db import db
import uuid
from forms import UpdateStockForm
from sqlalchemy import desc, asc
from sqlalchemy.orm import aliased

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash("Unauthorized", "danger")
            return redirect(url_for('web.home'))
        return f(*args, **kwargs)
    return decorated_function

# Create a blueprint for admin routes
admin = Blueprint('admin', __name__)

# Route to Admin Page
@admin.route("/admin")
@login_required
@admin_required
def admin_page():
    # Query all users from the database
    all_users = User.query.all()
    # Query all stocks from the database
    all_stocks = Stock.query.all()

    form = UpdateStockForm()
    form.stock_id.choices = [(stock.id, f"{stock.symbol} - {stock.company}") for stock in all_stocks]

    if form.validate_on_submit():
        stock = Stock.query.get(form.stock_id.data)
        if stock:
            stock.price = form.new_price.data
            stock.is_manual = form.is_manual.data
            stock.fluctuation_multiplier = form.fluctuation_multiplier.data
            db.session.commit()
            flash(f"Stock {stock.symbol} updated successfully!", "success")
        else:
            flash("Stock not found", "danger")
        
        return redirect(url_for('admin.admin_page'))

    # Return render template
    return render_template(
        'admin.html', 
        all_users=all_users, 
        all_stocks=all_stocks, 
        form=form
    )

# Transaction Table Route for AJAX
@admin.route("/admin/transactions/data")
@login_required
@admin_required
def transaction_data():
    # Pagination parameters
    user_pagination = current_user.pagination or 10
    page = request.args.get('start', 0, type=int) // user_pagination + 1 # Adjust for ceil
    per_page = request.args.get('length', user_pagination, type=int)

    # Handle "All" option in pagination
    if per_page == -1:
        per_page = None

    # Map column indexes to corresponding columns or expressions
    column_map = {
        '0': Transaction.order_number,
        '1': User.username,
        '2': Stock.symbol,
        '3': Transaction.type,
        '4': Transaction.quantity,
        '5': Transaction.price,
        '6': Transaction.amount,
        '7': Transaction.timestamp
    }

    # Sorting parameters
    sort_column_index = request.args.get('order[0][column]', '7') # Default to timestamp
    sort_column = column_map.get(sort_column_index, Transaction.timestamp)
    sort_direction = request.args.get('order[0][dir]', 'desc')

    # Determine sorting direction
    sort_order = desc if sort_direction == 'desc' else asc

    # Fetch and sort transactions
    transactions_query = db.session.query(
        Transaction,
        Stock.symbol.label('symbol'),
        User.username.label('username')
    ).join(
        Stock, 
        Stock.id == Transaction.stock
    ).join(
        User,
        User.id == Transaction.user
    )

    # Apply search filtering
    search_value = request.args.get('search[value]', '').strip()
    if search_value:
        transactions_query = transactions_query.filter(
            (Transaction.order_number.ilike(f'%{search_value}%')) |
            (Stock.symbol.ilike(f'%{search_value}%')) |
            (User.username.ilike(f'%{search_value}%')) |
            (Transaction.type.ilike(f'%{search_value}%'))
        )

    # Apply sorting logic
    transactions_query = transactions_query.order_by(
        sort_order(sort_column)
    )

    # Apply pagination
    if per_page:
        transactions_paginated = transactions_query.paginate(
            page=page, 
            per_page=per_page
        )
        transactions_items = transactions_paginated.items
        total_records = transactions_query.count()
        total_filtered = transactions_paginated.total
    else:
        transactions_items = transactions_query.all()
        total_records = total_filtered = len(transactions_items)

    # Prepare the response data
    transactions_data = [
        {
            "order_number": transaction.order_number,
            "symbol": symbol,
            "username": username,
            "type": transaction.type,
            "quantity": transaction.quantity,
            "price": transaction.price,
            "amount": transaction.amount,
            "timestamp": transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for transaction, symbol, username in transactions_items
    ]

    response = {
        "draw": request.args.get('draw', type=int),
        "recordsTotal": total_records,
        "recordsFiltered": total_filtered,
        "data": transactions_data
    }

    return jsonify(response)



""" 
MANUAL ROUTES
"""

# Update transaction order numbers if they are null
@admin.route("/null_transactions_update")
@login_required
@admin_required
def populate_order_numbers():
    # Fetch all transactions with null order numbers
    transactions = Transaction.query.filter(Transaction.order_number.is_(None)).all()

    if not transactions:
        print("No transactions with null order numbers found.")
        return "No transactions to update."

    for transaction in transactions:
        # Assign a unique UUID to the order_number field
        transaction.order_number = str(uuid.uuid4())

    # Commit the changes to the database
    db.session.commit()
    print(f"Updated {len(transactions)} transactions with new order numbers.")

    return "Order numbers populated successfully."