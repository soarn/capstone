from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from db.db_models import Transaction, db, Stock, StockHistory
from flasgger import swag_from
from functools import wraps

def json_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "User is not authenticated"}), 403
        return f(*args, **kwargs)
    return decorated_function

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
                    format: numeric
                    description: Stock price
                    example: 150.25
                  quantity:
                    type: integer
                    description: Quantity of stock available
                    example: 100
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
                        format: numeric
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
          format: Numeric
        required: true
        description: Stock price
        example: 150.25
      - in: path
        name: quantity
        schema:
          type: integer
        required: true
        description: Quantity of stock available
        example: 100
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
                  example: Stock with this symbol already exists
    """
    try:
        new_stock = Stock(symbol=symbol, company=company, price=float(price), quantity=float(quantity))
        db.session.add(new_stock)
        db.session.commit()
        return jsonify({'message': f"Stock {symbol} added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Route to get stock history
@api_v1.route('/stock-history/<period>', methods=['GET'])
@json_login_required
def get_stock_history(period):
    """
    Get historical stock data and user's transaction data for a for a specific stock and time period
    ---
    tags:
      - Stocks
    parameters:
      - in: path
        name: period
        schema:
          type: string
          enum: ["1D", "1W", "1M", "3M, "6M", "1Y", "all"]
        required: true
        description: Time period for historical stock data
      - in: query
        name: stock_id
        schema:
          type: integer
        required: true
        description: Stock ID to fetch the data for
    responses:
      200:
        description: Historical stock data and user's transaction data for the selected period
        content:
          application/json:
            schema:
              type: object
              properties:
                history:
                  type: array
                  items:
                    type: object
                    properties:
                      timestamp_unix:
                        type: integer
                        description: Unix timestamp
                        example: 1636540800
                      price:
                        type: number
                        format: numeric
                        example: 150.25
                transactions:
                  type: array
                  items:
                    type: object
                    properties:
                      timestamp:
                        type: string
                        format: date-time
                        example: 2024-11-10T12:00:00Z
                      price:
                        type: number
                        format: numeric
                        example: 150.25
                      quantity:
                        type: integer
                        example: 10
                      type:
                        type: string
                        enum: ["buy", "sell"]
                        example: buy
      403:
        description: User is not authenticated
        content:
          application/json:
            schema:
              type: object
    """
    stock_id = request.args.get("stock_id", type=int)
    if not stock_id:
        return jsonify({"error": "Stock ID is required"}), 400
    
    # Fetch the stock's history
    history = StockHistory.query.filter_by(stock_id=stock_id)

    # Fetch the current user's transactions for this stock
    transactions = Transaction.query.filter_by(stock=stock_id, user=current_user.id)

    # Filter based on the period
    period_mapping = {
        "1D": timedelta(days=1),
        "1W": timedelta(weeks=1),
        "1M": timedelta(weeks=4),
        "3M": timedelta(weeks=12),
        "6M": timedelta(weeks=26),
        "1Y": timedelta(weeks=52),
    }
    start_time = datetime.now() - period_mapping.get(period, timedelta(days=0)) if period in period_mapping else None
    
    if start_time:
        start_unix = int(start_time.timestamp())
        history = history.filter(StockHistory.timestamp_unix >= start_unix)
        transactions = transactions.filter(Transaction.timestamp_unix >= start_unix)

    history_data = [{
        "timestamp_unix": h.timestamp_unix, 
        "price": h.price,
        "open_price": h.open_price,
        "close_price": h.close_price if h.close_price else h.price,
        "high_price": h.high_price,
        "low_price": h.low_price,
        "volume": h.volume or 0
    } for h in history]
    transaction_data = [{
        "timestamp_unix": t.timestamp_unix,
        "price": t.price,
        "quantity": t.quantity,
        "type": t.type
    } for t in transactions]

    return jsonify({"history": history_data, "transactions": transaction_data})

@api_v1.route('/user-transactions', methods=['GET'])
@json_login_required
def get_user_transactions():
    """
    Get all transactions for the current user
    ---
    tags:
      - Transactions
    responses:
      200:
        description: A list of all transactions for the current user
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  order_number:
                    type: string
                    description: Order number
                    example: "22be3d16-b3be-468a-825e-b5bf6cf2cd45"
                  stock:
                    type: string
                    description: Stock symbol
                    example: AAPL
                  price:
                    type: number
                    description: Stock price
                    example: 150.25
                  type:
                    type: string
                    description: Transaction type (buy/sell)
                    example: buy
                  quantity:
                    type: integer
                    description: Quantity of stock
                    example: 10
                    type: number
                  amount:
                    description: Transaction amount
                    example: 1502.50
                  timestamp:
                    type: integer
                    description: Unix timestamp
                    example: 1636540800
      403:
        description: User is not authenticated
        content:
          application/json:
            schema:
              type: object
    """
    transactions = Transaction.query.filter_by(user=current_user.id).all()
    stock_ids = [t.stock for t in transactions if t.stock]
    stocks = Stock.query.filter(Stock.id.in_(stock_ids)).all()
    stock_map = {stock.id: stock.symbol for stock in stocks}
    transaction_list = [{
        "order_number": t.order_number,
        "stock": stock_map.get(t.stock, None),
        "price": t.price if t.price else None,
        "type": t.type,
        "quantity": t.quantity if t.quantity else None,
        "amount": t.amount if t.amount else None,
        "timestamp_unix": t.timestamp_unix
    } for t in transactions]

    return jsonify(transaction_list)
