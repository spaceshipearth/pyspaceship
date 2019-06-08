import logging
from flask import render_template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from spaceship.models.mission import Mission
from . import app

log = logging.getLogger('spaceship.email')

def send(to_emails, subject, html_content, from_email='gaia@spaceshipearth.org'):
  if not app.config['IN_PRODUCTION']:
    log.info("Sending email:")
    log.info(html_content)
  try:
    message = Mail(
      from_email=from_email,
      to_emails=to_emails,
      subject=subject,
      html_content=html_content)
    sg = SendGridAPIClient(app.config['SENDGRID_KEY'])
    response = sg.send(message)
  except Exception as e:
    # TODO: instrument send failures
    log.error('Unhandled exception sending email: %s', e)

def send_mission_start(mission_id, started_at):
  mission = Mission.query.get(mission_id)
  if not (mission and mission.is_active):
    log.warning(f'not sending mission start email for inactive mission {mission_id}')
    return

  # the start time has changed, so a different thing will actually
  # send the email
  if mission.started_at != started_at:
    log.warning(f'not sending mission start email for {mission} since start time has changed')
    return

  # if we got here, we should actually send an email
  emails = [m.email for m in mission.team.members]
  subject = 'Synchronize your watches, the mission begins!'
  content = render_template('email_mission_start.html', mission=mission)

  send(
    to_emails=emails,
    subject=subject,
    html_content=content,
  )
