from datetime import datetime
from flask import Blueprint, current_app, render_template, request, redirect, flash, url_for, jsonify
from flask_login import current_user, login_required
from functools import wraps
from utils import get_market_status
from db.db_models import Stock, StockHistory, User, Transaction, AdminSettings
from db.db import db
import uuid
from forms import UpdateStockForm, CreateStockForm, UpdateMarketForm
from sqlalchemy import desc, asc
from market import reschedule_market_close
from flask_babel import format_datetime
import pytz

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

    with current_app.app_context():
        market_status = get_market_status(current_app)

    # Initialize forms
    updateForm = UpdateStockForm()
    updateForm.stock_id.choices = [(stock.id, f"{stock.symbol} - {stock.company}") for stock in all_stocks]
    newForm = CreateStockForm()
    updateMarketForm = UpdateMarketForm()

    # Return render template
    return render_template(
        'admin.html', 
        all_users=all_users, 
        all_stocks=all_stocks,
        update_form=updateForm,
        add_form=newForm,
        update_market_form=updateMarketForm,
        market_status=market_status
    )

# Route to handle the update stock form
@admin.route("/admin/update_stock", methods=['POST'])
@login_required
@admin_required
def update_stock():
    all_stocks = Stock.query.all()

    # Instantiate the form
    updateForm = UpdateStockForm()
    updateForm.stock_id.choices = [(stock.id, f"{stock.symbol} - {stock.company}") for stock in all_stocks]

    if updateForm.validate_on_submit():
        stock = Stock.query.get(updateForm.stock_id.data)
        if stock:
            stock.price = updateForm.new_price.data
            stock.is_manual = updateForm.is_manual.data
            stock.fluctuation_multiplier = updateForm.fluctuation_multiplier.data
            db.session.commit()
            flash(f"Stock {stock.symbol} updated successfully!", "success")
        else:
            flash("Stock not found", "danger")
        
    return redirect(url_for('admin.admin_page'))
    
# Route to handle the create stock form
@admin.route("/admin/create_stock", methods=['POST'])
@login_required
@admin_required
def create_stock():

    # Instantiate the form
    newForm = CreateStockForm()
    
    if newForm.validate_on_submit():
        if not Stock.query.filter_by(symbol=newForm.symbol.data).first():
            stock = Stock(
                company=newForm.company.data,
                symbol=newForm.symbol.data,
                quantity=newForm.quantity.data,
                price=newForm.price.data,
            )
            db.session.add(stock)
            db.session.commit()
            flash(f"Stock ${stock.symbol} added successfully!", "success")
        else:
            flash("Invalid form data", "danger")

    return redirect(url_for('admin.admin_page'))

# Route to handle the market update form
@admin.route("/admin/update_market", methods=['POST'])
@login_required
@admin_required
def update_market():
    # Instantiate the form
    form = UpdateMarketForm()

    if form.validate_on_submit():
        settings = AdminSettings.query.first()
        if not settings:
            settings = AdminSettings()
            db.session.add(settings)

        settings.market_open = form.open.data
        settings.market_close = form.close.data
        settings.open_days_list = form.open_days.data
        settings.close_on_holidays = form.close_on_holidays.data

        db.session.commit()

        # Reschedule the market close job
        reschedule_market_close(current_app.scheduler, current_app)
        
        flash("Market settings updated successfully!", "success")
    else:
        flash("Failed to update market settings. Please check your inputs.", "danger")
    
    return redirect(url_for('admin.admin_page'))

# Transaction Table Route for AJAX
@admin.route("/admin/transactions/data")
@login_required
@admin_required
def transaction_data():
    user_time_zone = request.cookies.get('user_time_zone', 'UTC')
    tz = pytz.timezone(user_time_zone)
    user_locale = request.cookies.get('user_locale', 'en')

    print(f"User Time Zone: {user_time_zone}")
    print(f"tz: {tz}")
    print(f"User Locale: {request.cookies.get('user_locale', 'en')}")

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
        '7': Transaction.timestamp_unix
    }

    # Sorting parameters
    sort_column_index = request.args.get('order[0][column]', '7') # Default to timestamp
    sort_column = column_map.get(sort_column_index, Transaction.timestamp_unix)
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
        Stock.id == Transaction.stock,
        isouter=True # Left join (include transactions without stock)
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
            "quantity": transaction.quantity if transaction.quantity > 0 else None,
            "price": transaction.price,
            "amount": transaction.amount,
            "timestamp": transaction.timestamp
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

# Update unix timestamps
@admin.route("/update_unix_timestamps")
@login_required
@admin_required
def populate_unix_timestamps():
    try:
        histories = StockHistory.query.all()
        for history in histories:
            if history.timestamp:
                history.timestamp_unix = int(history.timestamp.timestamp())
        db.session.commit()

        transactions = Transaction.query.all()
        for transaction in transactions:
            if transaction.timestamp:
                transaction.timestamp_unix = int(transaction.timestamp.timestamp())
        db.session.commit()

        users = User.query.all()
        for user in users:
            if user.created_at:
                user.created_at_unix = int(user.created_at.timestamp())
            if user.last_login:
                user.last_login_unix = int(user.last_login.timestamp())
        db.session.commit()

        print("Unix timestamps updated successfully.")
        return "Unix timestamps updated successfully."
    
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return f"An error occurred: {e}", 500
