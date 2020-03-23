"""empty message

Revision ID: 966e100f2c89
Revises: 58f62c2f0614
Create Date: 2016-10-25 21:48:27.108656

"""

# revision identifiers, used by Alembic.
revision = '966e100f2c89'
down_revision = '58f62c2f0614'

from alembic import op
import sqlalchemy as sa


def upgrade():
	op.drop_column('large_request', 'request')
	op.add_column('large_request', sa.Column('request', sa.Text(4294967295), nullable=False))


def downgrade():
    pass
