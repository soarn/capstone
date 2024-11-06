from datetime import datetime, time as dt_time
import random
import holidays
from threading import Thread
from db.db_models import Stock, StockHistory, AdminSettings
from db.db import db
from apscheduler.schedulers.background import BackgroundScheduler

nyse_holidays = holidays.NYSE()

# Automatic Price Fluctuation and Stock Quantity Updates
def update_stock_prices():
    settings = AdminSettings.query.first()
    now = datetime.now().time()
    current_day = now.strftime('%A')

    # Check if the market is open based on the day, time, and holiday setting
    if (settings and 
        current_day in settings.open_days and
        settings.market_open <= now.time() <= settings.market_close and
        not (settings.close_on_holidays and now.date() in nyse_holidays)):
        
        stocks = Stock.query.all()
        for stock in stocks:
            if not stock.is_manual:
                fluctuation = random.unform(-0.01, 0.01) # Random fluctuation between -1% and 1%
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


# Record Stock History every 5 minutes
def record_stock_history():
    with db.app_context():
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

# Scheduler Configuration and Start
def start_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_stock_prices, 'interval', minutes=5, id='price_update')
    scheduler.add_job(record_stock_history, 'interval', minutes=5, id='history_recording')

    # Start the scheduler
    scheduler.start()

    # Attach to Flask app
    app.scheduler = scheduler

    # Shut down the scheduler when exiting the app
    @app.before_request
    def initialize_scheduler():
        app.before_request_funcs[None].remove(initialize_scheduler)
        with app.app_context():
            # Check if the database has market hours configured
            settings = AdminSettings.query.first()
            if not settings:
                settings = AdminSettings(
                    market_open=dt_time(8, 0),
                    market_close=dt_time(16, 0)
                )
                db.session.add(settings)
                db.session.commit()

    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        if scheduler.running:
            scheduler.shutdown()
