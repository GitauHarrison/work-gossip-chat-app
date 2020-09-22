from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm
from flask import render_template, redirect, url_for, flash, request, g
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from datetime import datetime
from flask_babel import _, get_locale

@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html', title = 'Home')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember = form.remember_me.data)    
        flash(_('You have logged in successfully!'))
        return redirect(url_for('home'))
    return render_template('login.html', title = 'Home', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('You have been registered successfully! Log in to continue.'))
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username = username).first_or_404()
    return render_template('profile.html', title = 'Profile', user = user)

@app.route('/edit_profile', methods = ['GET', 'POST'])
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved!'))
        return redirect(url_for('profile', username = current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title = 'Edit Profile', form = form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

@app.route('/follow.<username>', methods = 'POST')
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash(_('User %()s not found'), username = username)
            return redirect(url_for('profile', username = username))
        if user == current_user:
            flash(_('You cannot follow yourself'))
            return redirect(url_for('profile', username = username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are now following %()s'), username = username)
        return redirect(url_for('profile', username = username))
    else:
        return redirect(url_for('home'))

@app.route('/unfollow/<username>', methods = ['POST'])
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit()    :
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash(_('User %()s not found'), username = username)
            return redirect(url_for('profile', username = username))
        if user == current_user:
            flash(_('You cannot unfollow yourself'))
            return redirect(url_for('profile', username = username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %()s'), username = username)
        return redirect(url_for('profile', username = username))
    else:
        return redirect(url_for('home'))