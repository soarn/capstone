from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import current_user, login_required
from functools import wraps
from db.db_models import Stock, User, Transaction
from db.db import db
import uuid

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

    # Pass the users and stocks to the template
    return render_template('admin.html', all_users=all_users, all_stocks=all_stocks)

# Route to update stock information
@admin.route("/admin/update-stock", methods=['POST'])
@login_required
@admin_required
def admin_update_stock():
    stock_id = request.form['stock_id']
    new_price = request.form['new_price']
    # is_manual = request.form['is_manual'] == 'on'
    is_manual = 'is_manual' in request.form
    fluctuation_multiplier = request.form['fluctuation_multiplier']

    stock = Stock.query.get(stock_id)
    if stock:
        if is_manual:
            stock.manual_price = float(new_price)
            stock.is_manual = True
            stock.price = float(new_price)
        else:
            stock.is_manual = False
        
        stock.fluctuation_multiplier = float(fluctuation_multiplier)
        db.session.commit()
    
    flash("Stock updated successfully!", "success")
    return redirect(url_for('admin.admin_page'))

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