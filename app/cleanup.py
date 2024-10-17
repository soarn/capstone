from datetime import datetime, timedelta
from threading import Thread
import time
from db.db_models import StockHistory
from db.db import db

# Delete stock history older than 20 minutes
def delete_old_stock_history(app):
    while True:
        with app.app_context():
            threshold_time = datetime.now() - timedelta(minutes=20)
            StockHistory.query.filter(StockHistory.timestamp < threshold_time).delete()
            db.session.commit()
        
        time.sleep(300) # Cleanup every 5 minutes

def start_cleanup_task(app):
    Thread(target=delete_old_stock_history, args=(app,), daemon=True).start()