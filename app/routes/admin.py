from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import current_user, login_required
from functools import wraps
from db.db_models import Stock, User, Transaction
from db.db import db
import uuid
from forms import UpdateStockForm

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
    
    # Pass the users and stocks to the template
    return render_template('admin.html', all_users=all_users, all_stocks=all_stocks, form=form)

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