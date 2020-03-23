"""empty message

Revision ID: 15b0fe720940
Revises: b7df41979e23
Create Date: 2016-10-12 14:56:01.779573

"""

# revision identifiers, used by Alembic.
revision = '15b0fe720940'
down_revision = 'b7df41979e23'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('patients_active',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('hour', sa.Integer(), nullable=True),
    sa.Column('unit_floor', sa.String(length=100), nullable=True),
    sa.Column('number_active', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_active_date'), 'patients_active', ['date'], unique=False)
    op.create_index(op.f('ix_patients_active_hour'), 'patients_active', ['hour'], unique=False)
    op.create_index(op.f('ix_patients_active_unit_floor'), 'patients_active', ['unit_floor'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_patients_active_unit_floor'), table_name='patients_active')
    op.drop_index(op.f('ix_patients_active_hour'), table_name='patients_active')
    op.drop_index(op.f('ix_patients_active_date'), table_name='patients_active')
    op.drop_table('patients_active')
    ### end Alembic commands ###