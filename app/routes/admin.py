from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import current_user, login_required
from functools import wraps
from db.db_models import Stock, User
from db.db import db

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