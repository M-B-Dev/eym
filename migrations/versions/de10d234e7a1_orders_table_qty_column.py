"""orders table qty column

Revision ID: de10d234e7a1
Revises: 7f330a536273
Create Date: 2020-02-16 22:50:17.102470

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de10d234e7a1'
down_revision = '7f330a536273'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('qty', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'qty')
    # ### end Alembic commands ###
