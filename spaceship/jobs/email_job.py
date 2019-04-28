from .base_job import BaseJob

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .. import app

class EmailJob(BaseJob):
  @classmethod
  def perform(cls, to_emails, subject, html_content, from_email='gaia@spaceshipearth.org'):
    message = Mail(
      from_email=from_email,
      to_emails=to_emails,
      subject=subject,
      html_content=html_content)

    if app.config['IN_PRODUCTION']:
      sg = SendGridAPIClient(app.config['SENDGRID_KEY'])
      response = sg.send(message)
    else:
      cls.log().info(f"Sending email to {to_emails} subject {subject}:")
      cls.log().info(html_content)

