"""
user
date created: 2019-04-26 03:41:50.661142
"""


def upgrade(migrator):
    migrator.add_column('user', 'email_confirmed', 'bool', default=False)

def downgrade(migrator):
    migrator.drop_column('user', 'email_confirmed')
