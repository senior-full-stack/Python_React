"""empty message

Revision ID: d733999c96ff
Revises: 845112b789b9
Create Date: 2016-05-09 10:21:55.067677

"""

# revision identifiers, used by Alembic.
revision = 'd733999c96ff'
down_revision = '845112b789b9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_patient_name'), 'patient', ['name'], unique=False)
    op.alter_column('patient', 'medical_record_number', new_column_name='pa_id', existing_type=sa.String(100))
    op.add_column('patient', sa.Column('medical_record_number', sa.String(length=100), nullable=True))
    op.drop_index('ix_patient_medical_record_number', table_name='patient')
    op.create_index(op.f('ix_patient_medical_record_number'), 'patient', ['medical_record_number'], unique=True)
    op.create_index(op.f('ix_patient_pa_id'), 'patient', ['pa_id'], unique=True)
    op.add_column('patient_history', sa.Column('pa_id', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_patient_history_pa_id'), 'patient_history', ['pa_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_patient_pa_id'), table_name='patient')
    op.drop_index(op.f('ix_patient_medical_record_number'), table_name='patient')
    op.drop_column('patient', 'medical_record_number')
    op.drop_index(op.f('ix_patient_name'), table_name='patient')
    op.alter_column('patient', 'pa_id', new_column_name='medical_record_number', existing_type=sa.String(100))
    op.create_index('ix_patient_medical_record_number', 'patient', ['medical_record_number'], unique=True)
    op.drop_index(op.f('ix_patient_history_pa_id'), table_name='patient_history')
    op.drop_column('patient_history', 'pa_id')
    ### end Alembic commands ###
