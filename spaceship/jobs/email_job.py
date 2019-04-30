from .base_job import BaseJob

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import UnauthorizedError

from .. import app

class EmailJob(BaseJob):
  @classmethod
  def perform(cls, to_emails, subject, html_content, from_email='gaia@spaceshipearth.org'):
    cls.log().info(f"Sending email to {to_emails} subject {subject}")

    message = Mail(
      from_email=from_email,
      to_emails=to_emails,
      subject=subject,
      html_content=html_content)

    try:
      sg = SendGridAPIClient(app.config['SENDGRID_KEY'])
      response = sg.send(message)
    except UnauthorizedError:
      cls.log().info("Invalid credentials talking to sendgrid; email was:")
      cls.log().info(html_content)
