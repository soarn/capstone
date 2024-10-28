from datetime import datetime
from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from db.db_models import Portfolio, Stock, User, StockHistory
from db.db import db
from utils import fetch_bootswatch_themes, get_gravatar_url
import user_agents

globals = Blueprint('globals', __name__)

"""CONTEXT PROCESSORS """

# STOCK DATA
@globals.app_context_processor
def inject_stock_data():
    if current_user.is_authenticated:
        # Get the user's portfolio
        user_portfolio = (
            db.session.query(Portfolio, Stock)
            .filter(Portfolio.user == current_user.id)
            .join(Stock, Portfolio.stock == Stock.id)
            .all()
        )
        portfolio_stocks = [
            {"symbol": entry.Stock.symbol, "price": entry.Stock.price, "quantity": entry.Portfolio.quantity}
            for entry in user_portfolio
        ]
        
        if not portfolio_stocks:
            portfolio_stocks = Stock.query.all()

        all_stocks = Stock.query.all()
        stock_list = [{"symbol": stock.symbol, "price": stock.price} for stock in all_stocks]
        return {"stock_data": portfolio_stocks, "all_stocks": stock_list}
    else:
        # Fetch all stocks if not logged in
        all_stocks = Stock.query.all()
        stock_list = [{"symbol": stock.symbol, "price": stock.price} for stock in all_stocks]
        return {"stock_data": stock_list}

# THEME DATA
@globals.app_context_processor
def inject_themes():
    return {"themes": fetch_bootswatch_themes()}

# USER AGENT
@globals.app_context_processor
def inject_device_type():
    user_agent = request.headers.get("User-Agent")
    ua = user_agents.parse(user_agent)
    is_mobile = ua.is_mobile
    return {"is_mobile": is_mobile}