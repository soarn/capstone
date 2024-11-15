from flask import Flask
from flask_migrate import Migrate
from routes.globals import globals
from routes.web import web
from routes.api_v1 import api_v1
from routes.profile import profile
from routes.admin import admin
from datetime import timedelta, datetime
from db.db import db
from flasgger import Swagger
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from db.db_models import User
from utils import get_gravatar_url
from market import cleanup_intraday_fluctuations, cleanup_old_history, get_next_market_close, update_stock_prices, record_stocks
from flask_wtf.csrf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from flask_moment import Moment
from turbo_flask import Turbo
import os
import atexit

turbo = Turbo()

def create_app():
    # Initialize Flask App
    app = Flask(__name__)

    # Initialize Swagger
    swagger = Swagger(app)

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Flask-Login Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)  # If using remember me feature

    # CSRF Protection
    csrf = CSRFProtect(app)
    
    # Initialize the database with the app
    # Calls db from db\db.py to avoid circular imports
    db.init_app(app)

    # Initialize Migrate
    migrate = Migrate(app, db)

    # Initialize Moment
    moment = Moment(app)

    # Initialize Turbo
    turbo.init_app(app)
    # Register `turbo` in `current_app.extensions`
    app.extensions["turbo"] = turbo

    # Register blueprints
    app.register_blueprint(globals)
    app.register_blueprint(web)
    app.register_blueprint(api_v1)
    app.register_blueprint(profile)
    app.register_blueprint(admin)

    # Initialize Login Manager
    login_manager = LoginManager(app)
    # Redirect users to the login page if they are not logged in
    login_manager.login_view = 'web.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register the Gravatar URL function as a global Jinja variable
    app.jinja_env.globals.update(get_gravatar_url=get_gravatar_url)


    """
    BEGIN Scheduler Configuration
    """

    # Scheduler
    scheduler = BackgroundScheduler()
    app.scheduler = scheduler

    # Update stock prices and record stock history every minute
    scheduler.add_job(func=lambda: update_stock_prices(app), trigger=IntervalTrigger(minutes=1), id='update_stock_prices', name='Update stock prices every minute', replace_existing=True)
    # scheduler.add_job(func=lambda: update_stock_prices(app) if get_market_status(app) else None, trigger=IntervalTrigger(minutes=1), id='update_stock_prices', name='Update stock prices every minute', replace_existing=True)
    scheduler.add_job(func=lambda: record_stocks(app, shutdown=False), trigger=IntervalTrigger(minutes=1), id='record_stock_history', name='Record stock history every minute', replace_existing=True)

    # Schedule record_stocks at market close
    def schedule_record_stocks():
        next_close_time = get_next_market_close(app)
        if next_close_time:
            scheduler.add_job(func=lambda: record_stocks(app), trigger=DateTrigger(run_date=datetime.fromtimestamp(next_close_time)), id='record_stock_history_market_close', name='Record stock history at market close', replace_existing=True)
    
    schedule_record_stocks() # Schedule the job initially

    # Reschedule the job after every market close
    @scheduler.scheduled_job('cron', hour=0, minute=1)
    def reschedule_record_stocks():
        schedule_record_stocks()
    
    # Cleanup intraday fluctuations every day
    scheduler.add_job(func=lambda: cleanup_intraday_fluctuations(app), trigger=IntervalTrigger(days=1), id='cleanup_intraday_fluctuations', name='Cleanup intraday fluctuations older than retention period', replace_existing=True)
    # Cleanup old stock history every week
    scheduler.add_job(func=lambda: cleanup_old_history(app), trigger=IntervalTrigger(weeks=1), id='cleanup_old_history', name='Cleanup old stock history older than retention period', replace_existing=True)

    # Start the scheduler
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    atexit.register(lambda: record_stocks(app, shutdown=True))


    """
    END Scheduler Configuration
    """


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
