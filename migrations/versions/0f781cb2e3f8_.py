"""empty message

Revision ID: 0f781cb2e3f8
Revises: 996decc830a8
Create Date: 2019-01-24 16:00:44.656944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f781cb2e3f8'
down_revision = '996decc830a8'
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('geom')
    op.add_column('fields', sa.Column('job_status', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fields', 'job_status')
    op.create_table('geom',
    sa.Column('g', sa.NullType(), nullable=True),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    ### end Alembic commands ###
