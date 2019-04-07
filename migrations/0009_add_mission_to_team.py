"""
add mission to team
date created: 2019-04-07 04:28:25.365251
"""

def add_foreign_key(migrator, from_table, from_field, to_table, to_field, **kwargs):
    """Add a foreign key, which playhouse-moves doesn't seem to do properly."""
    migrator.add_column(from_table, from_field, 'int', **kwargs)
    playhouse_migrator = migrator.migrator
    playhouse_migrator.add_foreign_key_constraint(from_table, from_field, to_table, to_field).run()

def upgrade(migrator):
    add_foreign_key(migrator, 'team', 'mission_id', 'mission', 'id', null=True)
    migrator.add_column('team', 'mission_start_at', 'char', null=True)

def downgrade(migrator):
    migrator.drop_column('team', 'mission_id')
    migrator.drop_column('team', 'mission_start_at')
