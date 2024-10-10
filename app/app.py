from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from routes.web import web
from routes.api_v1 import api_v1
import os
from dotenv import load_dotenv
from db.db import db

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Initialize the database with the app
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(web)
    app.register_blueprint(api_v1)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
