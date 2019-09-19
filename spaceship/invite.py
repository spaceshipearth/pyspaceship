
from flask import render_template, url_for
import logging
import re
from typing import List, Optional

from spaceship import email, achievements
from spaceship.models import Invitation, Team, User

log = logging.getLogger('spaceship.invite')

class Invite:
  DEFAULT_SUBJECT = "Join my Spaceship Earth crew!"
  EMAIL_REGEX = re.compile(r"""[^@\s,]+@[^\s,]+""")

  @classmethod
  def default_message(cls, inviter: User, team: Team):
    return render_template('invite_crew.html', inviter=inviter, team=team)

  @classmethod
  def perform(cls, inviter: User, team_id: int, subject: str, message: str, emails: List[str]) -> Optional[str]:
    team = Team.query.get(team_id)
    if not team or team not in inviter.teams:
      return f'You are not authorized to invite crew onto team {team_id}'

    subject = subject if subject else cls.DEFAULT_SUBJECT
    message = message if message else cls.default_message(inviter, team)

    # quilljs needs <p><br></p> to show line breaks even though everything is in a paragraph
    # this creates extra line breaks in gmail so just strip it out
    message = message.replace('<p><br></p>', '')

    if not emails:
      return f'List a few folks to invite!'

    # an email is anything containing an `@` character, separated by whitespace and/or commas
    for invited_email in cls.EMAIL_REGEX.findall(emails):
      iv = Invitation(
        inviter=inviter,
        team=team,
        invited_email=invited_email,
        message=message,
        status='sent')
      iv.save()

      # each recipient sees a unique invite link
      invite_url = url_for('accept_invitation', key=iv.key_for_sharing, _external=True)
      if 'href="join"' in message:
        html_content = message.replace('href="join"', f'href="{invite_url}"')
      else:
        # if the user deleted the invite link, put it at the bottom
        html_content = f'{message}\n<p><a href="{invite_url}">Click here to join</a></p>'

      try:
        email.send.delay(
          to_emails=invited_email,
          subject=subject,
          html_content=html_content,
        )
      except Exception as e:
        log.exception(e.args)
        return "Failed to send email; try again?"

    achievements.invite_crew(inviter)
