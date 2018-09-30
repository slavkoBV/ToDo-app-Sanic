"""Create table Tasks

Revision ID: 16f2ceadd075
Revises: 
Create Date: 2018-09-30 14:17:49.571886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16f2ceadd075'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer, unique=True, autoincrement=True, primary_key=True),
        sa.Column('title', sa.String(30)),
        sa.Column('description', sa.String(100)),
        sa.Column('status', sa.Enum("To Do", "In Progress", "Review", "Done")))


def downgrade():
    pass
