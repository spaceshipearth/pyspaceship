"""
create table missiongoal
date created: 2019-05-04 20:40:35.201100
"""


def upgrade(migrator):
  with migrator.create_table('missiongoal') as table:
    table.primary_key('id')
    table.foreign_key('AUTO', 'mission_id', on_delete=None, on_update=None, references='mission.id')
    table.foreign_key('AUTO', 'goal_id', on_delete=None, on_update=None, references='goal.id')
    table.integer('week')
    table.char('created_at')
    table.char('deleted_at', null=True)


def downgrade(migrator):
    migrator.drop_table('missiongoal')
