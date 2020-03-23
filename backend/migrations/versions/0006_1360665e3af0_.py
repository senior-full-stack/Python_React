"""empty message

Revision ID: 1360665e3af0
Revises: e4b46379841e
Create Date: 2016-05-18 16:28:33.223937

"""

# revision identifiers, used by Alembic.
revision = '1360665e3af0'
down_revision = 'e4b46379841e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patient_activation', sa.Column('sensors_collected', sa.Boolean(), nullable=True))
    op.add_column('patient_activation', sa.Column('sensors_not_collected_reason', sa.Text(), nullable=True))
    op.add_column('patient_activation', sa.Column('date_of_record', sa.DateTime(), nullable=True))
    op.alter_column('body_location', 'outcome', new_column_name='wound_outcome', existing_type=sa.Text())
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('patient_activation', 'sensors_not_collected_reason')
    op.drop_column('patient_activation', 'sensors_collected')
    op.drop_column('patient_activation', 'date_of_record')
    op.alter_column('body_location', 'wound_outcome', new_column_name='outcome', existing_type=sa.Text())
    ### end Alembic commands ###
