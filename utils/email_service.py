from flask_mail import Message
from extensions import mail
from flask import render_template

def send_email(subject:str,email_template:str,recipients:list[str],values:dict):
    template_path = f"mail-templates/{email_template}.html"
    html = render_template(template_path, **values)
    email = Message(
        subject=subject,
        recipients=recipients,
        html=html,
    )
    mail.send(email)