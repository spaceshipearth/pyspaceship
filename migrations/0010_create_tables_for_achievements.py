"""
create tables for achievements
date created: 2019-04-14 11:26:51.649506
"""


def upgrade(migrator):
    with migrator.create_table('teamachievement') as table:
        table.primary_key('id')
        table.foreign_key('AUTO', 'team_id', on_delete=None, on_update=None, references='team.id')
        table.foreign_key('AUTO', 'mission_completed_id', on_delete=None, on_update=None, references='mission.id', null=True)
        table.char('name')
        table.char('created_at')
        table.char('deleted_at', null=True)

    with migrator.create_table('userachievement') as table:
        table.primary_key('id')
        table.foreign_key('AUTO', 'user_id', on_delete=None, on_update=None, references='user.id')
        table.char('name')
        table.char('created_at')
        table.char('deleted_at', null=True)


def downgrade(migrator):
    migrator.drop_table('userachievement')
    migrator.drop_table('teamachievement')
