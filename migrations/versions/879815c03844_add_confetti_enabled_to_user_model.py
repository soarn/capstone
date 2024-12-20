"""Add confetti_enabled to User model

Revision ID: 879815c03844
Revises: 2375b65e6001
Create Date: 2024-10-20 13:49:02.054787

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '879815c03844'
down_revision = '2375b65e6001'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confetti_enabled', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('confetti_enabled')
        
    # ### end Alembic commands ###
