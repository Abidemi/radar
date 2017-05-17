"""add weight to GroupObservation

Revision ID: 483215d716db
Revises: 72c21b8fa484
Create Date: 2017-04-19 13:35:57.255745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '483215d716db'
down_revision = '72c21b8fa484'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('group_observations', sa.Column('weight', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('group_observations', 'weight')
    # ### end Alembic commands ###