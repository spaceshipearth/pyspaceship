"""merge survey and goal migrations

Revision ID: 6f32f51871d2
Revises: 8f7566ab3e16, c28413616223
Create Date: 2019-09-29 00:46:05.563038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f32f51871d2'
down_revision = ('8f7566ab3e16', 'c28413616223')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
