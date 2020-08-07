"""empty message

Revision ID: 996decc830a8
Revises: 7fa7267eed8c
Create Date: 2018-10-05 16:02:38.018065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '996decc830a8'
down_revision = '7fa7267eed8c'
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('growers', sa.Column('retail', sa.String(length=250), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('growers', 'retail')
    ### end Alembic commands ###