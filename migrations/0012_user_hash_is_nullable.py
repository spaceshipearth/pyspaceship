"""
user hash is nullable
date created: 2019-04-26 04:19:56.041129
"""


def upgrade(migrator):
  migrator.execute_sql('ALTER TABLE user MODIFY password_hash VARCHAR(255) NULL')

def downgrade(migrator):
  migrator.execute_sql('ALTER TABLE user MODIFY password_hash VARCHAR(255) NOT NULL')
