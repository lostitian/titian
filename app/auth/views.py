from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ForgetPasswordForm, PasswordOnlyForm
from ..models import User, Role
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid usename or password.')
	return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash("Now logged out")
	return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
	form=RegistrationForm()
	if form.validate_on_submit():
		user=User(email=form.email.data, username=form.username.data, password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token=user.generate_confirmation_token()
		send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
		flash('A confirmation email has been sent to you by email.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('Confirmed successfully!')
	else:
		flash('The confirmation link is invalid of has expired.')
	return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
	if current_user.is_authenticated \
		and not current_user.confirmed \
		and request.endpoint[:5] != 'auth.' \
		and request.endpoint != 'static':
		return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
	token=current_user.generate_confirmation_token()
	send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
	flash('A new email has been sent to you.')
	return redirect(url_for('main.index'))

@auth.route('/change', methods=['GET','POST'])
@login_required
def change():
	form=ChangePasswordForm()
	if form.validate_on_submit():
		if current_user is not None and current_user.verify_password(form.old_password.data) == True:
			current_user.password=form.password.data
			flash('Password has been changed!')
			return redirect(url_for('main.index'))
		flash('Your old password was wrong!')
	return render_template('auth/changepassword.html',form=form)

@auth.route('/forget', methods=['GET', 'POST'])
def forget():
	form=ForgetPasswordForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user:
			token=user.generate_forget_token()
			send_email(user.email, 'Reset your password', 'auth/email/forget', token=token)
			return redirect(url_for('main.index'))
		flash("Email is not exist")
	return render_template('auth/forget.html',form=form)

@auth.route('/forget/<token>', methods=['GET', 'POST'])
def forget_reset(token):
	try:
		email=User.confirm_forget(token)
	except:
		return render_template('404.html')
	form=PasswordOnlyForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=email).first()
		user.password=form.password.data
		db.session.add(user)
		db.session.commit()
		flash('Succeed, now login!')
		return redirect('auth/login')
	return render_template('auth/PasswordOnly.html',form=form)

