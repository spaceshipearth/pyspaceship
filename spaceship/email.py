from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

from . import app

def send(to_emails, subject, html_content, from_email='gaia@spaceshipearth.org'):
    if not app.config['IN_PRODUCTION']:
        app.logger.info("Sending email:")
        app.logger.info(html_content)
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
        app.logger.error("Exception occured sending email")
 