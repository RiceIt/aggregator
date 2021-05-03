"""add_adding_filters

Revision ID: f60f22c87473
Revises: 1fb476ed055d
Create Date: 2021-05-02 13:05:40.896787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f60f22c87473'
down_revision = '1fb476ed055d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('adding_filters', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'adding_filters')
    # ### end Alembic commands ###
