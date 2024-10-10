from flask import Blueprint, jsonify
from db.db_models import Stock, db

# Create a blueprint for API version 1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Route to get all stocks
@api_v1.route('/stocks', methods=['GET'])
def get_stocks():
    stocks = Stock.query.all()  # Query all stocks from the database
    stock_list = [{"symbol": stock.symbol, "company": stock.company, "price": stock.price, "quantity": stock.quantity} for stock in stocks]
    return jsonify(stock_list)

# Route to add a new stock
@api_v1.route('/add-stock/<symbol>/<company>/<price>/<quantity>', methods=['POST'])
def add_stock(symbol, company, price, quantity):
    try:
        new_stock = Stock(symbol=symbol, company=company, price=float(price), quantity=float(quantity))
        db.session.add(new_stock)
        db.session.commit()
        return jsonify({'message': f"Stock {symbol} added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
