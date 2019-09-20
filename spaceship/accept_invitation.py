
from flask import render_template

from spaceship import email
from spaceship.models import Invitation, Team, TeamUser, User

def accept_invitation(cls, invitation: Invitation, user: User) -> Team:
  team: Team = invitation.team
  if user in team.members:
    return team

  # add to team
  tu = TeamUser(team=team, user=user)
  tu.save()

  # mark the invite as accepted
  invitation.mark_accepted()
  invitation.save()

  # tell captain about new user
  captain = team.captain
  email.send.delay(
    to_emails=[captain.email],
    subject='Your crew is growing!',
    html_content=render_template('crew_growing_email.html', team=team),
  )

  return team
