"""
create table team
date created: 2019-03-29 02:49:01.113410
"""


def upgrade(migrator):
    with migrator.create_table('team') as table:
        table.primary_key('id')
        table.foreign_key('AUTO', 'captain_id', on_delete=None, on_update=None, references='user.id')
        table.char('name', max_length=255)
        table.char('created_at')
        table.char('deleted_at', null=True)


def downgrade(migrator):
    migrator.drop_table('team')
