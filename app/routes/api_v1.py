from flask import Blueprint, jsonify
from db.db_models import Stock, db
from flasgger import swag_from

# Create a blueprint for API version 1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Route to get all stocks
@api_v1.route('/stocks', methods=['GET'])
def get_stocks():
    """
    Get a list of all stocks
    ---
    tags:
      - Stocks
    responses:
      200:
        description: A list of all stocks
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  symbol:
                    type: string
                    description: Stock symbol
                    example: AAPL
                  company:
                    type: string
                    description: Company name
                    example: Apple Inc.
                  price:
                    type: number
                    format: float
                    description: Stock price
                    example: 150.25
                  quantity:
                    type: integer
                    description: Quantity of stock available
                    example: 1000
        schema:
                id: stocks
                properties:
                    symbol:
                        type: string
                        description: The stock symbol
                    company:
                        type: string
                        description: The company name
                    price:
                        type: number
                        description: The stock price
                    quantity:
                        type: number
                        description: The quantity of the stock
    """
    stocks = Stock.query.all()  # Query all stocks from the database
    stock_list = [{"symbol": stock.symbol, "company": stock.company, "price": stock.price, "quantity": stock.quantity} for stock in stocks]
    return jsonify(stock_list)

# Route to add a new stock
@api_v1.route('/add-stock/<symbol>/<company>/<price>/<quantity>', methods=['POST'])
def add_stock(symbol, company, price, quantity):
    """
    Add a new stock to the database
    ---
    tags:
      - Stocks
    parameters:
      - in: path
        name: symbol
        schema:
          type: string
        required: true
        description: Stock symbol
      - in: path
        name: company
        schema:
          type: string
        required: true
        description: Company name
      - in: path
        name: price
        schema:
          type: number
        required: true
        description: Stock price
        example: 150.25
      - in: path
        name: quantity
        schema:
          type: integer
        required: true
        description: Quantity of stock available
        example: 1000
    responses:
      201:
        description: Stock added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Stock AAPL added successfully
      400:
        description: Bad request or error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Stock with this symbol already exists"
    """
    try:
        new_stock = Stock(symbol=symbol, company=company, price=float(price), quantity=float(quantity))
        db.session.add(new_stock)
        db.session.commit()
        return jsonify({'message': f"Stock {symbol} added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
