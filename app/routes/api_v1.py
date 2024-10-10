from flask import Blueprint, jsonify

# Create a blueprint for API version 1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1.route('/stocks', methods=['GET'])
def get_stocks():
    # Placeholder response, eventually this will return stock data
    return jsonify({"message": "List of stocks"})
