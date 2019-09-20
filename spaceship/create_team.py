
from spaceship import names, achievements
from spaceship.models import Team, TeamUser

def create_team(user):
  """given a user, makes that user a captain of a new team"""
  team = Team(captain=user, name=names.name_team())
  team.save()

  # also become a member on that team
  tu = TeamUser(user=user, team=team)
  tu.save()

  # user became a captain! celebrate!
  achievements.become_captain(user)

  return team
