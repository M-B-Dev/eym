"""updated user table

Revision ID: 3dfeb33d7a02
Revises: 0067739f37ab
Create Date: 2020-02-09 19:26:43.916573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3dfeb33d7a02'
down_revision = '0067739f37ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('address', sa.String(length=140), nullable=True))
    op.add_column('user', sa.Column('status', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'status')
    op.drop_column('user', 'address')
    # ### end Alembic commands ###