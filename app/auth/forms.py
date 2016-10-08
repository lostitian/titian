from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
	email = StringField('Email', validators=[Required(), Length(1,64), Email()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('keep me logged in')
	submit = SubmitField('Log in')

class RegistrationForm(Form):
	email = StringField('Email', validators=[Required(), Length(1,64), Email()])
	username = StringField('Username', validators=[
		Required(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Username must have only letters, numbers, dots, or underscores')])
	password = PasswordField('Password', validators=[Required(), EqualTo('password2',message='Passwords must match')])
	password2 = PasswordField('Confirm Password', validators=[Required()])
	submit = SubmitField('Register')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registed.')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use.')

class ChangePasswordForm(Form):
	old_password = PasswordField('Your Old Password', validators=[Required()])
	password = PasswordField('New Password', validators=[Required(), EqualTo('password2',message='Passwords must match')])
	password2 = PasswordField('Confirm Password', validators=[Required()])
	submit = SubmitField('Change Password')

class ForgetPasswordForm(Form):
	email = StringField('Email', validators=[Required(), Length(1,64), Email()])
	submit = SubmitField('Submit')

class PasswordOnlyForm(Form):
	password=PasswordField('New Password', validators=[Required(), EqualTo('password2',message='Passwords must match')])
	password2=PasswordField('Confirm Password', validators=[Required()])
	submit=SubmitField('Submit')