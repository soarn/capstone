"""fix divergent migration branches

Revision ID: 0262de377bcc
Revises: 1753236f8495, 840af6d1b6fe
Create Date: 2024-11-09 22:13:14.676793

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0262de377bcc'
down_revision = ('1753236f8495', '840af6d1b6fe')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
