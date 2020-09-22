from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequest, ResetPasswordForm
from flask import render_template, redirect, url_for, flash, request, g, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from datetime import datetime
from flask_babel import _, get_locale
from guess_language import guess_language
from app.translate import translate
from app.email import send_password_reset_email

@app.route('/', methods = ['GET', 'POST'])
@app.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
    form = PostForm() 
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body = form.post.data, author = current_user, language = language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('home'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('home', page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('home', page = posts.prev_num) \
        if posts.has_prev else None
    return render_template('home.html', title = 'Home', form = form, posts = posts.items, prev_url = prev_url, next_url = next_url)

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
    form = EmptyForm()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('profile', username = username, page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('profile', username = username, page = posts.prev_num) \
        if posts.has_prev else None
    return render_template('profile.html', title = 'Profile', user = user, form = form, posts = posts.items, next_url = next_url, prev_url = prev_url)

@app.route('/explore')
def explore():    
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('explore', page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page = posts.prev_num) \
        if posts.has_prev else None
    return render_template('home.html', title = 'Explore', posts = posts.items, next_url = next_url, prev_url = prev_url)

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

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash(_('User %(username)s not found', username = username))
            return redirect(url_for('profile', username = username))
        if user == current_user:
            flash(_('You cannot follow yourself'))
            return redirect(url_for('profile', username = username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are now following %(username)s', username = username))
        return redirect(url_for('profile', username = username))
    else:
        return redirect(url_for('home'))

@app.route('/unfollow/<username>', methods = ['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit()    :
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash(_('User %(username)s not found', username = username))
            return redirect(url_for('profile', username = username))
        if user == current_user:
            flash(_('You cannot unfollow yourself'))
            return redirect(url_for('profile', username = username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s', username = username))
        return redirect(url_for('profile', username = username))
    else:
        return redirect(url_for('home'))

@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})

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

@app.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password_request(token):
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