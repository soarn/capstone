from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required
from db.db_models import Stock, User
from db.db import db

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
def portfolio():
    return render_template('portfolio.html')

@web.route("/buy")
def buy():
    return render_template('buy.html')

@web.route("/sell")
def sell():
    return render_template('sell.html')

# @web.route("/profile")
# def profile():
#     return render_template('profile.html')

# LOGIN ROUTE
@web.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Log the user in
            login_user(user)
            flash("Login successful!", "success")
            # Redirect to the profile page after login
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