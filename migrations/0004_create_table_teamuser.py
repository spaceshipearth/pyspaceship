"""
create table teamuser
date created: 2019-03-29 03:01:36.237297
"""


def upgrade(migrator):
    with migrator.create_table('teamuser') as table:
        table.primary_key('id')
        table.foreign_key('AUTO', 'user_id', on_delete=None, on_update=None, references='user.id')
        table.foreign_key('AUTO', 'team_id', on_delete=None, on_update=None, references='team.id')
        table.char('created_at')
        table.char('deleted_at', null=True)


def downgrade(migrator):
    migrator.drop_table('teamuser')
