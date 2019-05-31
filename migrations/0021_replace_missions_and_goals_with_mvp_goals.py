"""
replace missions and goals with mvp goals
date created: 2019-05-24 03:16:26.067360
"""

def upgrade(migrator):
    migrator.execute_sql('delete from pledge');
    migrator.execute_sql('delete from missiongoal');
    migrator.execute_sql('delete from mission');
    migrator.execute_sql('delete from goal');

    migrator.execute_sql(
        '''insert into goal (short_description, category, created_at)
                       values  
                        ("Don't eat beef" , "diet", "2019-05-23 10:00:00.000000"),
                        ("Eat a vegeterian diet" , "diet", "2019-05-23 10:00:00.000000"),
                        ("Eat a vegan diet" , "diet", "2019-05-23 10:00:00.000000")
        ''')

def downgrade(migrator):
    # from past import future
    pass