"""
add category to goal
date created: 2019-05-11 23:10:47.565837
"""

def upgrade(migrator):
  migrator.add_column('goal', 'category', 'char', default='diet')

def downgrade(migrator):
  migrator.drop_column('goal', 'category')
