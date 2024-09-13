import smtplib
import ssl
from email.message import EmailMessage

from app.settings import settings


def send_mail(template: EmailMessage):
    context = ssl.create_default_context()
    with smtplib.SMTP(settings.email.HOST, settings.email.PORT) as server:
        server.starttls(context=context)
        server.login(settings.email.LOGIN, settings.email.PASSWORD)
        server.send_message(template)
