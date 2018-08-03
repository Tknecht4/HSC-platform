"""empty message

Revision ID: 6a53e107fd7b
Revises: c253d5398d47
Create Date: 2018-07-27 18:16:48.492878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a53e107fd7b'
down_revision = 'c253d5398d47'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fields', sa.Column('avg_n', sa.Float(), nullable=True))
    op.add_column('fields', sa.Column('avg_yield', sa.Float(), nullable=True))
    op.add_column('fields', sa.Column('crop_year', sa.Integer(), nullable=True))
    op.add_column('fields', sa.Column('harvest_score', sa.Integer(), nullable=True))
    op.add_column('fields', sa.Column('is_vr', sa.Boolean(), nullable=True))
    op.add_column('fields', sa.Column('map_blob', sa.LargeBinary(), nullable=True))
    op.add_column('fields', sa.Column('report_path', sa.String(length=250), nullable=True))
    op.add_column('fields', sa.Column('variety', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fields', 'variety')
    op.drop_column('fields', 'report_path')
    op.drop_column('fields', 'map_blob')
    op.drop_column('fields', 'is_vr')
    op.drop_column('fields', 'harvest_score')
    op.drop_column('fields', 'crop_year')
    op.drop_column('fields', 'avg_yield')
    op.drop_column('fields', 'avg_n')
    # ### end Alembic commands ###
