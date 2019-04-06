"""
bake test mission
date created: 2019-04-06 17:18:27.656882
"""


def upgrade(migrator):
    cursor = migrator.execute_sql(
        '''insert into mission (id, title, short_description, created_at)
                       values (0, "Plant based diet", "Eat plants", "2019-04-06 10:00:00.000000")''')
    mission_id = cursor.lastrowid
    migrator.execute_sql(
        '''insert into goal (mission_id, week, short_description, primary_for_mission, created_at)
                       values ({mid}, 0, "Cook a plant-based meal for yourself and friends/family", false, "2019-04-06 10:00:00.000000"),
                              ({mid}, 0, "Make a plant-based protein replacement like seitan", false, "2019-04-06 10:00:00.000000"),
                              ({mid}, 0, "Go out to a vegan/vegetarian restaurant", false, "2019-04-06 10:00:00.000000"),
                              ({mid}, 1, "At a restaurant, order a plant-based meal instead of meat", true, "2019-04-06 10:00:00.000000"),
                              ({mid}, 2, "Cook a meal for yourself with a plant-based meat substitute (tofu sausage, etc)", true, "2019-04-06 10:00:00.000000"),
                              ({mid}, 3, "Cook a plant-based meal for yourself and your friends/family", true, "2019-04-06 10:00:00.000000"),
                              ({mid}, 4, "Eat three plant-based meals", true, "2019-04-06 10:00:00.000000")'''.format(mid=mission_id))

def downgrade(migrator):
    migrator.execute_sql('delete from goal')
    migrator.execute_sql('delete from mission')
