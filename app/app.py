from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from routes.web import web
from routes.api_v1 import api_v1
from routes.profile import profile
import os
from dotenv import load_dotenv
from db.db import db
from flasgger import Swagger

def create_app():
    # Initialize Flask App
    app = Flask(__name__)

    # Initialize Swagger
    swagger = Swagger(app)

    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Initialize the database with the app
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(web)
    app.register_blueprint(api_v1)
    app.register_blueprint(profile)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
