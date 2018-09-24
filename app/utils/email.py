from threading import Thread

from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail


def _send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(recipients, subject, template, sync=False, **kwargs):
    msg = Message(
        subject=subject,
        sender=current_app.config.get('MAIL_SENDER'),
        recipients=recipients,
        charset='utf-8')
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    real_app_instance = current_app._get_current_object()

    if sync:
        mail.send(msg)
    else:
        Thread(target=_send_async_email,
               args=(real_app_instance, msg)).start()
