"""empty message

Revision ID: 2b8622f90e52
Revises: 8983509660c6
Create Date: 2018-07-19 20:28:16.467594

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b8622f90e52'
down_revision = '8983509660c6'
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fields', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'fields', 'users', ['user_id'], ['id'])
    op.add_column('growers', sa.Column('created', sa.DateTime(), nullable=True))
    op.add_column('growers', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'growers', 'users', ['user_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'growers', type_='foreignkey')
    op.drop_column('growers', 'user_id')
    op.drop_column('growers', 'created')
    op.drop_constraint(None, 'fields', type_='foreignkey')
    op.drop_column('fields', 'user_id')
    ### end Alembic commands ###
