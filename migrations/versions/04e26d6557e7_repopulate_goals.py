"""repopulate-goals

Revision ID: 04e26d6557e7
Revises: 7d648ddc717b
Create Date: 2019-07-18 20:25:43.876372

"""
from alembic import op
import sqlalchemy as sa
from datetime import date


# revision identifiers, used by Alembic.
revision = '04e26d6557e7'
down_revision = '7d648ddc717b'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM mission_goal")
    op.execute("DELETE FROM goal")
    op.execute("INSERT INTO goal values(1, 'Eat no beef for the duration of the mission.', 'diet', null, null)")
    op.execute("INSERT INTO goal values(2, 'Eat vegetarian food exclusively.', 'diet', null, null)")
    op.execute("INSERT INTO goal values(3, 'Eat vegan food exclusively.', 'diet', null, null)")



def downgrade():
    op.execute("DELETE FROM mission_goal")
    op.execute("DELETE FROM goal")
