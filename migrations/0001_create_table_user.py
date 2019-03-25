"""
create table user
date created: 2019-03-25 11:06:13.223558
"""


def upgrade(migrator):
    with migrator.create_table('user') as table:
        table.primary_key('id')
        table.char('email', max_length=255, unique=True)
        table.char('password_hash', max_length=255)
        table.datetime('created_at')
        table.datetime('deleted_at', null=True)


def downgrade(migrator):
    migrator.drop_table('user')
