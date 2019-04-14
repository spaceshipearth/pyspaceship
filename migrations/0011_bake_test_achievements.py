"""
bake test achievements
date created: 2019-04-14 11:33:00.751505
"""


def upgrade(migrator):
    cursor = migrator.execute_sql(
        '''insert into achievement (id, name, short_description, created_at)
                       values (0, "Complete Plant based diet", "Awarded for completing the Plant based diet mission", "2019-04-14 10:00:00.000000"),
                              (1, "Pledge for a goal", "Awarded for pledging to complete a goal", "2019-04-14 10:00:00.000000"),
                              (2, "Fulfill a pledge", "Awarded for fulfilling a pledge", "2019-04-14 10:00:00.000000"),
                              (3, "Become a captain", "Awarded for becoming a captain", "2019-04-14 10:00:00.000000"),
                              (4, "Invite crew", "Awarded for inviting crew to join", "2019-04-14 10:00:00.000000")''')


def downgrade(migrator):
    migrator.execute_sql('delete from achievement')
