"""
add team_id to mission
date created: 2019-05-24 03:43:40.214101
"""
from peewee import *

def upgrade(migrator):
    migrator.execute_sql('ALTER TABLE mission ADD team_id INT NOT NULL DEFAULT 0')
    migrator.execute_sql('ALTER TABLE mission ADD CONSTRAINT fk_team_id FOREIGN KEY (team_id) REFERENCES team(id)');

def downgrade(migrator):
    migrator.drop_column('mission', 'team_id')
