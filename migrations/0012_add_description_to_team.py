"""
add description to team
date created: 2019-04-26 06:27:46.338009
"""
def upgrade(migrator):
    migrator.add_column('team', 'description', 'text', default='Best. Crew. Ever.')

def downgrade(migrator):
    migrator.drop_column('team', 'description')
