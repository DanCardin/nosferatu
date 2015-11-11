"""empty message

Revision ID: 3799f04aa3d
Revises: 418e9228da3
Create Date: 2015-11-11 16:36:20.672070

"""

# revision identifiers, used by Alembic.
revision = '3799f04aa3d'
down_revision = '418e9228da3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('nodes', sa.Column('relay_status', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('nodes', 'relay_status')
    ### end Alembic commands ###
