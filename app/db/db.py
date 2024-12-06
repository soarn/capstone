# Avoid circular import by defining the database in a separate file
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
