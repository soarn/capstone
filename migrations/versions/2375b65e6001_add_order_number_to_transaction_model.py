"""Add order_number to Transaction model

Revision ID: 2375b65e6001
Revises: 
Create Date: 2024-10-20 12:36:46.948762

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from sqlalchemy import table, column
import uuid

# revision identifiers, used by Alembic.
revision = '2375b65e6001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Check if 'order_number' column already exists
    conn = op.get_bind()
    result = conn.execute(text("SHOW COLUMNS FROM transaction LIKE 'order_number'")).fetchone()

    if not result:
        # Add the 'order_number' column if it doesn't exist
        with op.batch_alter_table('transaction', schema=None) as batch_op:
            batch_op.add_column(sa.Column('order_number', sa.String(length=36), nullable=True))

        # Create a temporary table reference for transactions
        transaction_table = table(
            'transaction',
            column('id', sa.Integer),
            column('order_number', sa.String(36))
        )

        # Populate existing rows with unique order numbers
        result = conn.execute(sa.select([transaction_table.c.id]))

        for row in result:
            order_number = str(uuid.uuid4())  # Generate a unique UUID
            conn.execute(
                transaction_table.update()
                .where(transaction_table.c.id == row.id)
                .values(order_number=order_number)
            )

        # Make the order_number column non-nullable and add the UNIQUE constraint
        with op.batch_alter_table('transaction', schema=None) as batch_op:
            batch_op.alter_column('order_number', nullable=False)
            batch_op.create_unique_constraint('uq_transaction_order_number', ['order_number'])


def downgrade():
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_constraint('uq_transaction_order_number', type_='unique')
        batch_op.drop_column('order_number')
