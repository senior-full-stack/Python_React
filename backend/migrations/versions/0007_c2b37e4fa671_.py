"""empty message

Revision ID: c2b37e4fa671
Revises: 1360665e3af0
Create Date: 2016-05-31 08:59:29.742657

"""

# revision identifiers, used by Alembic.
revision = 'c2b37e4fa671'
down_revision = '1360665e3af0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('diagnosis', sa.Column('past_diagnosis_patient_id', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'diagnosis', ['past_diagnosis_patient_id'])
    op.create_foreign_key(None, 'diagnosis', 'patient', ['past_diagnosis_patient_id'], ['id'])
    op.add_column('patient_history', sa.Column('past_diagnosis', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('patient_history', 'past_diagnosis')
    op.drop_constraint('diagnosis_ibfk_2', 'diagnosis', type_='foreignkey')
    op.drop_constraint('past_diagnosis_patient_id', 'diagnosis', type_='unique')
    op.drop_column('diagnosis', 'past_diagnosis_patient_id')
    ### end Alembic commands ###
