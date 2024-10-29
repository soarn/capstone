"""Add pagination setting to User model

Revision ID: 9b569d065b84
Revises: 037f50fc5f4f
Create Date: 2024-10-28 10:52:57.871681

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9b569d065b84'
down_revision = '4a95f48135a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pagination', sa.Integer(), nullable=False, server_default='10'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('pagination')

    # ### end Alembic commands ###