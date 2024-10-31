"""Update transactions table to accomodate for tracking user balance changes

Revision ID: 840af6d1b6fe
Revises: d701d7cab213
Create Date: 2024-10-30 12:53:01.458142

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '840af6d1b6fe'
down_revision = 'd701d7cab213'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.alter_column('order_number',
               existing_type=mysql.VARCHAR(length=36),
               nullable=False)
        batch_op.alter_column('stock',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('price',
               existing_type=mysql.FLOAT(),
               nullable=True)
        batch_op.create_unique_constraint(None, ['order_number'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('price',
               existing_type=mysql.FLOAT(),
               nullable=False)
        batch_op.alter_column('stock',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.alter_column('order_number',
               existing_type=mysql.VARCHAR(length=36),
               nullable=True)

    # ### end Alembic commands ###
