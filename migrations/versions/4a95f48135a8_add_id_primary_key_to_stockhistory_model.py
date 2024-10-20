"""Add id primary key to StockHistory model

Revision ID: 4a95f48135a8
Revises: 879815c03844
Create Date: 2024-10-20 14:26:09.815006

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4a95f48135a8'
down_revision = '879815c03844'
branch_labels = None
depends_on = None


def upgrade():
    # Create a temporary table with the new schema, including 'id' as the primary key
    op.execute("""
        CREATE TABLE stock_history_temp (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            stock_id INT NOT NULL,
            timestamp DATETIME NOT NULL,
            price FLOAT NOT NULL,
            quantity FLOAT NOT NULL,
            CONSTRAINT fk_stock_id FOREIGN KEY (stock_id) REFERENCES stock (id)
        )
    """)

    # Copy data from the original table to the temporary table
    op.execute("""
        INSERT INTO stock_history_temp (stock_id, timestamp, price, quantity)
        SELECT stock_id, timestamp, price, quantity FROM stock_history
    """)

    # Drop the original table
    op.execute("DROP TABLE stock_history")

    # Rename the temporary table to the original table name
    op.execute("RENAME TABLE stock_history_temp TO stock_history")


def downgrade():
    # Create a temporary table with the original schema
    op.execute("""
        CREATE TABLE stock_history_temp (
            stock_id INT NOT NULL,
            timestamp DATETIME NOT NULL,
            price FLOAT NOT NULL,
            quantity FLOAT NOT NULL,
            PRIMARY KEY (stock_id, timestamp),
            CONSTRAINT fk_stock_id FOREIGN KEY (stock_id) REFERENCES stock (id)
        )
    """)

    # Copy data from the modified table to the temporary table
    op.execute("""
        INSERT INTO stock_history_temp (stock_id, timestamp, price, quantity)
        SELECT stock_id, timestamp, price, quantity FROM stock_history
    """)

    # Drop the modified table
    op.execute("DROP TABLE stock_history")

    # Rename the temporary table back to the original name
    op.execute("RENAME TABLE stock_history_temp TO stock_history")