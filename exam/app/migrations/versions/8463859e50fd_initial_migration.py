"""Initial migration.

Revision ID: 8463859e50fd
Revises: 
Create Date: 2023-06-07 15:22:39.051971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8463859e50fd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_roles'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles')
    # ### end Alembic commands ###
