from datetime import datetime
from flask import render_template,session,redirect,url_for, flash, abort, request
from flask_login import login_required, current_user

from . import main
from .. import db
from ..models import User, Permission, Post, Comment, Role
from .forms import PostForm, EditProfileForm, EditProfileAdminForm, CommentForm
from ..decorators import admin_required, permission_required



@main.route('/', methods=['GET', 'POST'])
def index():
	form=PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		post = Post(body=form.body.data, author=current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page)
	posts = pagination.items
	return render_template('index.html', form=form, posts=posts, pagination=pagination)

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	page = request.args.get('page',1,type=int)
	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page)
	posts = pagination.items
	return render_template('user.html', user=user, posts=posts, pagination=pagination)

@main.route('/post/<int:id>',methods=['GET', 'POST'])
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data,
			post=post,
			author=current_user._get_current_object())
		db.session.add(comment)
		flash('Your comment has been sent')
		return redirect(url_for('.post', id=post.id, page=-1))
	page = request.args.get('page', 1, type=int)
	if page==-1:
		page = (post.comments.count() - 1) / 20 + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=20, error_out=False)
	comments = pagination.items
	return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name=form.name.data
		current_user.location=form.location.data
		current_user.about_me=form.about_me.data
		db.session.add(current_user)
		flash('Your profile has been updated.')
		return redirect(url_for('.user', username=current_user.username))
	form.name.data=current_user.name
	form.location.data=current_user.location
	form.about_me.data=current_user.about_me
	return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>',methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash('The profile has been changed.')
		return redirect(url_for('.user',username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data =user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)

@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		flash('The post has been updated.')
		return redirect(url_for('.post', id=post.id))
	form.body.data = post.body
	return render_template('edit_post.html', form=form)

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page)
	comments = pagination.items
	return render_template('moderate.html', comments=comments, pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))

@main.route('/delete/<int:id>')
@login_required
def delete(id):
	post = Post.query.get_or_404(id)
	if current_user.is_administrator or current_user == post.author: 
		db.session.delete(post)
		flash('The post has been deleted.')
		return redirect(url_for('.index'))
	abort(403)