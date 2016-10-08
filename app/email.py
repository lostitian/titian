from flask import render_template
from flask_mail import Message
from . import mail
from manage import app

def send_email(to, subject, template, **kwargs):
	msg=Message(app.config['FLASK_MAIL_SUBJECT_PREFIX']+subject, sender=app.config['FLASK_MAIL_SENDER'], recipients=[to])
	msg.body=render_template(template + '.txt',**kwargs)
	mail.send(msg)