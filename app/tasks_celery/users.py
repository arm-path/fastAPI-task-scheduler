from email.message import EmailMessage

from pydantic import EmailStr

from app.mail.services import send_mail
from app.mail.templates import recovery_password_message, verify_email_message


def send_mail_recovery_password(email: EmailStr, username: str, confirmation_token: str) -> None:
    template_message: EmailMessage = recovery_password_message(email, username, confirmation_token)
    send_mail(template_message)


def send_mail_email_confirmation(email: EmailStr, token: str) -> None:
    template_message: EmailMessage = verify_email_message(email, token)
    send_mail(template_message)
