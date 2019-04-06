"""
models for missions and goals
date created: 2019-04-06 16:46:35.148039
"""

def upgrade(migrator):
    with migrator.create_table('mission') as table:
        table.primary_key('id')
        table.char('title')
        table.text('short_description')
        table.foreign_key('AUTO', 'prerequisite_id', references='mission.id', null=True)
        table.char('created_at')
        table.char('deleted_at', null=True)

    with migrator.create_table('goal') as table:
        table.primary_key('id')
        table.foreign_key('AUTO', 'mission_id', on_delete=None, on_update=None, references='mission.id')
        table.integer('week')
        table.text('short_description')
        table.bool('primary_for_mission')
        table.char('created_at')
        table.char('deleted_at', null=True)

def downgrade(migrator):
    migrator.drop_table('goal')
    migrator.drop_table('mission')
