"""
rebake test mission using join table
date created: 2019-05-04 20:52:40.627367
"""

def upgrade(migrator):
  migrator.execute_sql(
    '''insert into missiongoal (mission_id, goal_id, week, created_at)
       select goal.mission_id as mission_id,
              goal.id as goal_id,
              goal.week as week,
              goal.created_at as created_at
       from goal;''')

def downgrade(migrator):
  migrator.execute_sql('delete from missiongoal')
