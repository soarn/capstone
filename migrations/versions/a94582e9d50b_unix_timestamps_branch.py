"""unix-timestamps branch

Revision ID: a94582e9d50b
Revises: 4007435dca96
Create Date: 2024-11-10 16:53:23.892429

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a94582e9d50b'
down_revision = '4007435dca96'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stock_history', schema=None) as batch_op:
        batch_op.alter_column('timestamp_unix',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)

    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.alter_column('timestamp_unix',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('created_at_unix',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
        batch_op.alter_column('last_login_unix',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('last_login_unix',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('created_at_unix',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               existing_nullable=True)

    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.alter_column('timestamp_unix',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               existing_nullable=True)

    with op.batch_alter_table('stock_history', schema=None) as batch_op:
        batch_op.alter_column('timestamp_unix',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
