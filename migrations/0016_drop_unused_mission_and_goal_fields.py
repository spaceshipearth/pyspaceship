"""
drop unused mission and goal fields
date created: 2019-05-04 21:44:40.156692
"""

def add_foreign_key(migrator, from_table, from_field, to_table, to_field, **kwargs):
  """Add a foreign key, which playhouse-moves doesn't seem to do properly."""
  migrator.add_column(from_table, from_field, 'int', **kwargs)
  playhouse_migrator = migrator.migrator
  playhouse_migrator.add_foreign_key_constraint(from_table, from_field, to_table, to_field).run()

def upgrade(migrator):
  migrator.drop_column('goal', 'week')
  migrator.drop_column('goal', 'mission_id')
  migrator.drop_column('goal', 'primary_for_mission')
  migrator.drop_column('mission', 'prerequisite_id')

def downgrade(migrator):
  add_foreign_key(migrator, 'mission', 'prerequisite_id', 'mission', 'id', null=True)
  migrator.add_column('goal', 'primary_for_mission', 'bool', default=True)
  add_foreign_key(migrator, 'goal', 'mission_id', 'mission', 'id', null=True)
  migrator.add_column('goal', 'week', 'int', default=0)
  migrator.execute_sql(
    '''update goal g
       inner join missiongoal mg on g.id = mg.goal_id
       set g.week = mg.week, g.mission_id = mg.mission_id''')
