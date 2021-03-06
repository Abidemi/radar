"""add india ethnicity table

Revision ID: d4e81c8c52b9
Revises: 483215d716db
Create Date: 2017-05-05 15:14:47.754855

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4e81c8c52b9'
down_revision = '483215d716db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('india_ethnicities',
    sa.Column('id', postgresql.UUID(), server_default=sa.text(u'uuid_generate_v4()'), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('source_group_id', sa.Integer(), nullable=False),
    sa.Column('source_type', sa.String(), nullable=False),
    sa.Column('father_ancestral_state', sa.String(), nullable=True),
    sa.Column('father_language', sa.String(), nullable=True),
    sa.Column('mother_ancestral_state', sa.String(), nullable=True),
    sa.Column('mother_language', sa.String(), nullable=True),
    sa.Column('created_user_id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=False),
    sa.Column('modified_user_id', sa.Integer(), nullable=False),
    sa.Column('modified_date', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['modified_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['source_group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('india_ethnicity_patient_idx', 'india_ethnicities', ['patient_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('india_ethnicity_patient_idx', table_name='india_ethnicities')
    op.drop_table('india_ethnicities')
    # ### end Alembic commands ###
