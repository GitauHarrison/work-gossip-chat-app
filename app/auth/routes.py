from app.auth import bp
from app import db
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from app.models import User
from flask_babel import _
from app.auth.email import send_password_reset_email

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

@app.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_passwor(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset!'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', title = 'Reset Password', form = form)

@app.route('/reset_password_request', methods = ['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequest()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions on how to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title = 'Request Password Reset', form = form)