"""improved-pricing branch

Revision ID: 03914933722c
Revises: 0262de377bcc
Create Date: 2024-11-09 22:16:06.888873

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '03914933722c'
down_revision = '1753236f8495'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin_settings', schema=None) as batch_op:
        batch_op.alter_column('open_days',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.String(length=254),
               existing_nullable=True)

    with op.batch_alter_table('stock', schema=None) as batch_op:
        batch_op.alter_column('company',
               existing_type=mysql.VARCHAR(length=100),
               type_=sa.String(length=128),
               existing_nullable=False)
        batch_op.alter_column('price',
               existing_type=mysql.FLOAT(),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=False)
        batch_op.alter_column('quantity',
               existing_type=mysql.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=False)
        batch_op.alter_column('manual_price',
               existing_type=mysql.FLOAT(),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=True)

    with op.batch_alter_table('stock_history', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=mysql.DECIMAL(precision=10, scale=0),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=False)
        batch_op.alter_column('quantity',
               existing_type=mysql.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=False)

    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('marker_flag', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('marker_text', sa.String(length=254), nullable=True))
        batch_op.alter_column('price',
               existing_type=mysql.FLOAT(),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=True)
        batch_op.alter_column('amount',
               existing_type=mysql.FLOAT(),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.alter_column('amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=mysql.FLOAT(),
               existing_nullable=False)
        batch_op.alter_column('price',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=mysql.FLOAT(),
               existing_nullable=True)
        batch_op.drop_column('marker_text')
        batch_op.drop_column('marker_flag')

    with op.batch_alter_table('stock_history', schema=None) as batch_op:
        batch_op.alter_column('quantity',
               existing_type=sa.Integer(),
               type_=mysql.FLOAT(),
               existing_nullable=False)
        batch_op.alter_column('price',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=mysql.DECIMAL(precision=10, scale=0),
               existing_nullable=False)

    with op.batch_alter_table('stock', schema=None) as batch_op:
        batch_op.alter_column('manual_price',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=mysql.FLOAT(),
               existing_nullable=True)
        batch_op.alter_column('quantity',
               existing_type=sa.Integer(),
               type_=mysql.FLOAT(),
               existing_nullable=False)
        batch_op.alter_column('price',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=mysql.FLOAT(),
               existing_nullable=False)
        batch_op.alter_column('company',
               existing_type=sa.String(length=128),
               type_=mysql.VARCHAR(length=100),
               existing_nullable=False)

    with op.batch_alter_table('admin_settings', schema=None) as batch_op:
        batch_op.alter_column('open_days',
               existing_type=sa.String(length=254),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)

    # ### end Alembic commands ###