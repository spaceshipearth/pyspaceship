"""
create table usergoal
date created: 2019-04-06 18:49:38.765486
"""


def upgrade(migrator):
    with migrator.create_table('pledge') as table:
        table.primary_key('id')
        table.foreign_key('AUTO', 'user_id', on_delete=None, on_update=None, references='user.id')
        table.foreign_key('AUTO', 'goal_id', on_delete=None, on_update=None, references='goal.id')
        table.bool('fulfilled')
        table.char('start_at')
        table.char('end_at')
        table.char('created_at')
        table.char('deleted_at', null=True)


def downgrade(migrator):
    migrator.drop_table('pledge')
