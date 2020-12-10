## 이메일 발송 래퍼 기능.
from flask_mail import Message
from app import mail, app
from flask import render_template

# 이메일 발송 래퍼 기능.
def send_email(subject, sender, recipients, text_body, html_body ):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

# 비밀번호 재설정 이메일 보내기 기능
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email( '[Microblog] Reset Your Password',
                sender=app.config['ADMINS'][0],
                recipients=[user.email],
                text_body=render_template('email/reset_password.txt', user=user, token=token),
                html_body=render_template('email/reset_password.html', user=user, token=token))



