"""empty message

Revision ID: 845112b789b9
Revises: 74f9d453f026
Create Date: 2016-05-02 08:13:23.420981

"""

# revision identifiers, used by Alembic.
revision = '845112b789b9'
down_revision = '74f9d453f026'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patient', sa.Column('name', sa.String(length=100), nullable=True))
    op.add_column('patient_history', sa.Column('name', sa.String(length=100), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('patient_history', 'name')
    op.drop_column('patient', 'name')
    ### end Alembic commands ###
