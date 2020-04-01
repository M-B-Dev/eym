"""updated username

Revision ID: 3171758603a1
Revises: 3dfeb33d7a02
Create Date: 2020-02-12 20:44:43.064038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3171758603a1'
down_revision = '3dfeb33d7a02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_username', table_name='user')
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.create_index('ix_user_username', 'user', ['username'], unique=1)
    # ### end Alembic commands ###
