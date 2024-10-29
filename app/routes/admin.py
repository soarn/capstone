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
    

    """
    Transaction History
    """

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = current_user.pagination

    # Sorting parameters
    sort_column = request.args.get('sort', 'timestamp') # Default sorting column
    sort_direction = request.args.get('direction', 'desc') # Default sorting direction

    # Determine sorting order
    sort_order = desc if sort_direction == 'desc' else asc

    # Aliased tables
    StockAlias = aliased(Stock)
    UserAlias = aliased(User)

    # Mapping sort_column to the correct model and column
    sort_mapping = {
        'timestamp'   : Transaction.timestamp,
        'order_number': Transaction.order_number,
        'quantity'    : Transaction.quantity,
        'price'       : Transaction.price,
        'amount'      : Transaction.amount,
        'type'        : Transaction.type,
        'stock'       : StockAlias.symbol,
        'user'        : UserAlias.username
    }

    # Check if the requested sort column is valid
    if sort_column in sort_mapping:
        sort_field = sort_mapping[sort_column]
    else:
        # Fallback to default column
        sort_field = 'timestamp'
    
    # Log the sort column and order (for debugging)
    print(f"Sorting by: {sort_column} ({sort_direction})")
    print(f"Sorting by: {sort_field} ({sort_direction})")

    # Fetch paginated transactions with joins for stock symbol and user info
    transactions_paginated = (
        db.session.query(
            Transaction,
            StockAlias.symbol.label('stock_symbol'),
            UserAlias.username.label('username')
        )
        .join(StockAlias, Transaction.stock == StockAlias.id)
        .join(UserAlias, Transaction.user == UserAlias.id)
        .order_by(sort_order(sort_field))
        .paginate(page=page, per_page=per_page)
    )

    # Return render template
    return render_template(
        'admin.html', 
        all_users=all_users, 
        all_stocks=all_stocks, 
        form=form,
        transactions=transactions_paginated.items,
        pagination=transactions_paginated,
        sort_column=sort_column,
        sort_direction=sort_direction
    )

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