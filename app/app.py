from flask import Flask
from routes.web import web
from routes.api_v1 import api_v1

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(web)
app.register_blueprint(api_v1)

if __name__ == '__main__':
    app.run(debug=True)