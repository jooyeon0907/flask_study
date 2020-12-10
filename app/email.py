## 이메일 발송 래퍼 기능.
from flask_mail import Message
from app import mail

# 이메일 발송 래퍼 기능.
def send_email(subject, sender, recipients, text_body, html_body ):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


