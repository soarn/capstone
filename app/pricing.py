from datetime import datetime
import random
import holidays
from utils import get_market_status
from db.db_models import Stock, StockHistory, AdminSettings
from db.db import db

# Automatic Price Fluctuation and Stock Quantity Updates
def update_stock_prices(app):
    with app.app_context():
        # Check if the market is open based on the day, time, and holiday setting
        fluctuation = random.uniform(-0.01, 0.01) # Random fluctuation between -1% and 1%
        if (get_market_status(app) == "open"):

            stocks = Stock.query.all()
            for stock in stocks:
                if not stock.is_manual:
                    fluctuation = random.uniform(-0.01, 0.01) # Random fluctuation between -1% and 1%
                    new_price = stock.price * (1 + fluctuation * stock.fluctuation_multiplier)

                    # Adjust available quantity based on price change
                    if fluctuation < 0: # Price decreasing, simulate selling
                        stock.quantity += int(stock.quantity * random.uniform(0.01, 0.05)) # Increase available quantity
                    else: # Price increasing, simulate buying
                        stock.quantity -= int(stock.quantity * random.uniform(0.01, 0.05)) # Decrease available quantity

                    stock.quantity = max(stock.quantity, 0) # Prevent negative quantity
                    stock.price = round(new_price, 2)
            db.session.commit()

# Record Stock History every 5 minutes
def record_stock_history(app):
    with app.app_context():
        stocks = Stock.query.all()
        for stock in stocks:
            stock_history = StockHistory(
                stock_id=stock.id,
                price=stock.price,
                quantity=stock.quantity,
                timestamp=datetime.now()
            )
            db.session.add(stock_history)
        db.session.commit()
