"""empty message

Revision ID: e9c747b27da4
Revises: c2b37e4fa671
Create Date: 2016-06-06 11:08:29.138219

"""

# revision identifiers, used by Alembic.
revision = 'e9c747b27da4'
down_revision = 'c2b37e4fa671'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('diagnosis', sa.Column('hypertension', sa.Boolean(), nullable=True))
    op.add_column('diagnosis', sa.Column('malignancy', sa.Boolean(), nullable=True))
    op.add_column('medication', sa.Column('chemotherapy', sa.Boolean(), nullable=True))
    op.add_column('medication', sa.Column('radiation', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('medication', 'radiation')
    op.drop_column('medication', 'chemotherapy')
    op.drop_column('diagnosis', 'malignancy')
    op.drop_column('diagnosis', 'hypertension')
    ### end Alembic commands ###