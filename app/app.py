from flask import Flask
from routes import main

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(main)