"""
add name to user
date created: 2019-03-29 02:33:24.496832
"""
from peewee import CharField

def upgrade(migrator):
    migrator.add_column('user', 'name', CharField, max_length=255, default='')

def downgrade(migrator):
    migrator.drop_column('user', 'name')

