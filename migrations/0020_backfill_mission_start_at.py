"""
backfill mission start_at
date created: 2019-05-17 01:07:57.050728
"""


def upgrade(migrator):
  # missions with missing start_at will 500, reset missions one time to work around this
  migrator.execute_sql('update team set mission_id=null;')

def downgrade(migrator):
  pass
