# Market Simulation, Scheduling, and Cleanup
import random
from datetime import datetime, timedelta
import holidays
from utils import get_market_status
from db.db_models import Stock, StockHistory, AdminSettings
from db.db import db
from apscheduler.triggers.date import DateTrigger

# Automatic Price Fluctuation and Stock Quantity Updates
def update_stock_prices(app):
    """
    Updates stock prices with a random fluctuation, simulates market dynamics, 
    and ensures that quantities and prices are valid. Runs if the market is open.
    """
    with app.app_context():
        # Check if the market is open based on the day, time, and holiday setting
        if (get_market_status(app) == "open"):
            fluctuation = random.uniform(-0.01, 0.01) # Random fluctuation between -1% and 1%

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

# Record Stock History
def record_stocks(app):
    """
    Records stock history into the StockHistory table, ensuring 
    historical data is logged for analysis and charting purposes.
    """
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

# Get Next Market Close Time
def get_next_market_close(app):
    """
    Calculates the next market close time based on the current day, holiday, and AdminSettings.
    Returns a datetime object.
    """
    with app.app_context():
        settings = AdminSettings.query.first()
        if settings:
            now = datetime.now()
            market_close_today = datetime.combine(now.date(), settings.market_close)
            nyse_holidays = holidays.NYSE()

            # Check if market close today is valid
            if (now.time() > settings.market_close or # Market already closed
                now.strftime('%A') not in settings.open_days_list or # Not an open day
                (settings.close_on_holidays and now.date() in nyse_holidays)): # Holiday
                # Move to the next valid day
                market_close_today += timedelta(days=1)
                while (market_close_today.strftime('%A') not in settings.open_days_list or
                    (settings.close_on_holidays and market_close_today.date() in nyse_holidays)):
                    market_close_today += timedelta(days=1)
                
            return market_close_today
    return None

# Reschedule Record Stocks if Market Close Changes
def reschedule_market_close(scheduler, app):
    """
    Reschedules the record_stocks job if the market close time changes.
    """
    # Remove any existing market close jobs
    if scheduler.get_job('record_stock_history_market_close'):
        scheduler.remove_job('record_stock_history_market_close')
    
    # Schedule the job for the new market close time
    next_close_time = get_next_market_close(app)
    if next_close_time:
        scheduler.add_job(
            func=lambda: record_stocks(app),
            trigger=DateTrigger(run_date=next_close_time),
            id='record_stock_history_market_close',
            name='Record stock history at market close',
            replace_existing=True
        )

# Intraday Cleanup Task
def cleanup_intraday_fluctuations(app, retention_days=7):
    """
    Deletes intraday fluctuations older than the retention period.
    Retains daily closing prices for long-term analysis.
    """
    with app.app_context():
        # Calculate the threshold for intraday data retention
        threshold_date = datetime.now() - timedelta(days=retention_days)

        # Identify records to retain: daily market close
        daily_closes = db.session.query(
            StockHistory.stock_id,
            db.func.max(StockHistory.timestamp).label("latest_close")
        ).filter(
            StockHistory.timestamp < threshold_date
        ).group_by(
            StockHistory.stock_id, db.func.date(StockHistory.timestamp)
        ).subquery()

        # Delete all other intraday records older than the retention period
        deleted_rows = StockHistory.query.filter(
            StockHistory.timestamp < threshold_date
        ).filter(
            ~StockHistory.id.in_(
                db.session.query(daily_closes.c.latest_close)
            )
        ).delete(synchronize_session=False)

        db.session.commit()
        print(f"[CLEANUP] Deleted {deleted_rows} intraday records older than {threshold_date}")

# Historical Cleanup Task
def cleanup_old_history(app, retention_years=1):
    """
    Deletes historical stock records older than the retention period.
    """
    with app.app_context():
        # Calculate the threshold for long-term retention
        threshold_date = datetime.now() - timedelta(days=retention_years * 365)

        # Delete old records
        deleted_rows = StockHistory.query.filter(
            StockHistory.timestamp < threshold_date
        ).delete(synchronize_session=False)

        db.session.commit()
        print(f"[CLEANUP] Delete {deleted_rows} historical records older than {threshold_date}")