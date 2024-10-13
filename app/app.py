from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from routes.profile import profile
from routes.web import web
from routes.api_v1 import api_v1
import os
from datetime import timedelta
from dotenv import load_dotenv
from db.db import db
from flasgger import Swagger
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from db.db_models import User

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

    # Initialize the database with the app
    # Calls db from db\db.py to avoid circular imports
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(web)
    app.register_blueprint(api_v1)
    app.register_blueprint(profile)

    # Initialize Login Manager
    login_manager = LoginManager(app)
    # Redirect users to the login page if they are not logged in
    login_manager.login_view = 'web.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
