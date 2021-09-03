"""003

Revision ID: eb6e1e7348ba
Revises: 692af3ead7d8
Create Date: 2021-08-29 20:07:39.680366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb6e1e7348ba'
down_revision = '692af3ead7d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('times',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hour', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_times',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('time_id', sa.Integer(), nullable=False),
    sa.Column('mode', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['time_id'], ['times.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'time_id')
    )
    op.alter_column('users_categories', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('users_categories', 'category_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users_categories', 'category_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('users_categories', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_table('users_times')
    op.drop_table('times')
    # ### end Alembic commands ###
