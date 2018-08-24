"""empty message

Revision ID: abdec4a49fcf
Revises: 6a53e107fd7b
Create Date: 2018-08-23 18:00:52.855169

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'abdec4a49fcf'
down_revision = '6a53e107fd7b'
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('data', 'app_data')
    op.drop_column('data', 'yield_data')
    op.add_column('fields', sa.Column('app_data', sa.String(length=500), nullable=True))
    op.add_column('fields', sa.Column('map_img', sa.String(length=250), nullable=True))
    op.add_column('fields', sa.Column('plot_img', sa.String(length=250), nullable=True))
    op.add_column('fields', sa.Column('yield_data', sa.String(length=500), nullable=True))
    op.drop_column('fields', 'report_path')
    op.drop_column('fields', 'map_blob')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fields', sa.Column('map_blob', sa.BLOB(), nullable=True))
    op.add_column('fields', sa.Column('report_path', mysql.VARCHAR(length=250), nullable=True))
    op.drop_column('fields', 'yield_data')
    op.drop_column('fields', 'plot_img')
    op.drop_column('fields', 'map_img')
    op.drop_column('fields', 'app_data')
    op.add_column('data', sa.Column('yield_data', mysql.FLOAT(), nullable=True))
    op.add_column('data', sa.Column('app_data', mysql.FLOAT(), nullable=True))
    ### end Alembic commands ###
