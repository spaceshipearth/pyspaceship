"""
create table invitation
date created: 2019-03-30 16:08:07.924311
"""


def upgrade(migrator):
    with migrator.create_table('invitation') as table:
        table.primary_key('id')
        table.uuid('key_for_sharing')
        table.foreign_key('AUTO', 'inviter_id', on_delete=None, on_update=None, references='user.id')
        table.foreign_key('AUTO', 'team_id', on_delete=None, on_update=None, references='team.id')
        table.char('invited_email', max_length=255)
        table.text('message')
        table.char('status', max_length=16, null=True)
        table.char('created_at')
        table.char('deleted_at', null=True)


def downgrade(migrator):
    migrator.drop_table('invitation')
