"""slug_filter

Revision ID: 1fb476ed055d
Revises: 0b853773e60d
Create Date: 2021-05-02 12:02:48.306523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fb476ed055d'
down_revision = '0b853773e60d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('filters', sa.Column('slug', sa.String(length=255), nullable=True))
    op.drop_constraint('filters_name_key', 'filters', type_='unique')
    op.create_unique_constraint(None, 'filters', ['slug'])
    op.drop_constraint('users_osa_key', 'users', type_='unique')
    op.drop_column('users', 'osa')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('osa', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_unique_constraint('users_osa_key', 'users', ['osa'])
    op.drop_constraint(None, 'filters', type_='unique')
    op.create_unique_constraint('filters_name_key', 'filters', ['name'])
    op.drop_column('filters', 'slug')
    # ### end Alembic commands ###
