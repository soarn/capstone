from datetime import datetime
import random
import time
from threading import Thread
from db.db_models import Stock, StockHistory
from db.db import db

# Automatic Price Fluctuation and Stock Quantity Updates
def update_stock_prices(app):
    while True:
        with app.app_context():
            stocks = Stock.query.all()
            for stock in stocks:
                if not stock.is_manual:
                    fluctuation = random.uniform(-0.01, 0.01) # Random fluctuation between -1% and 1%
                    new_price = stock.price * (1 + fluctuation * stock.fluctuation_multiplier)

                    # Adjust available quantity based on price change
                    if fluctuation < 0: # Price decreasing, simulate selling
                        stock.quantity += int(stock.quantity * random.uniform(0.01, 0.05)) # Increase available quantity
                        # stock.quantity += int(stock.quantity * 0.05) ## If the above is too much
                    else: # Price increasing, simulate buying
                        stock.quantity -= int(stock.quantity * random.uniform(0.01, 0.05)) # Decrease available quantity
                        # stock.quantity -= int(stock.quantity * 0.05) ## If the above is too much

                    stock.quantity = max(stock.quantity, 0) # Prevent negative quantity
                    stock.price = round(new_price, 2)
                    db.session.commit()
        time.sleep(5) # Update prices every 5 seconds

def start_price_updater(app):
    Thread(target=update_stock_prices, args=(app,), daemon=True).start()

# Record Stock History
def record_stock_history(app):
    while True:
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

        time.sleep(60) # Record every minute
        #time.sleep(3600) ## Record every hour

def start_history_recorder(app):
    Thread(target=record_stock_history, args=(app,), daemon=True).start()
