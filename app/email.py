from flask_mail import Message
from app import mail, app
from flask import render_template

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        '[TinkerChatApp] Reset Your Password',
        sender = app.config['ADMINS'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', token = token, user = user),
        html_body = render_template('email/reset_password.html', token = token, user = user)
    )