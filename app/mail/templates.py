from email.message import EmailMessage

from pydantic import EmailStr

from app.settings import settings


def verify_email_message(email: EmailStr, token: str):
    template_message = EmailMessage()
    template_message.add_header('From', settings.email.LOGIN)
    template_message.add_header('To', settings.email.LOGIN)  # TODO: 'settings.email.LOGIN' edit 'email'.
    template_message.add_header('Subject', 'Подтверждение электронной почты')
    content = f"""
        <h1>Подтверждение электронной почты</h1>
        <p>Для подтверждения электронной почты, на сайте «{settings.site.NAME}», перейдите по ссылке:
        <a href="{settings.site.URL_ADDRESS}authentication/activate/{token}"> Подтвердить электронную почту </a>
         </p>
        """

    template_message.set_content(content, subtype='html')
    return template_message

def recovery_password_message(email: EmailStr, username: str, token: str):
    template_message = EmailMessage()
    template_message.add_header('From', settings.email.LOGIN)
    template_message.add_header('To', settings.email.LOGIN) # TODO: 'settings.email.LOGIN' edit 'email'.
    template_message.add_header('Subject', 'Восстановление пароля')
    content = f"""
            <h1>Восстановление пароля: {username}</h1>
            <p>Для восстановления пароля, на сайте «{settings.site.NAME}», перейдите по ссылке:
            <a href="{settings.site.URL_ADDRESS}authentication/recovery-password/edit/{token}"> Восстановить пароль </a>
             </p>
            """

    template_message.set_content(content, subtype='html')
    return template_message