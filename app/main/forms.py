from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l
from flask import request

class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators = [DataRequired()])
    about_me = TextAreaField(_l('About Me'), validators = [DataRequired(), Length(min = 0, max = 140)])
    submit = SubmitField(_l('Update Profile'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField(_l('Say Something'), validators = [DataRequired()])
    submit = SubmitField('Post Your Comment')

class SearchForm(FlaskForm):
    q = StringField(_('Search'), validators = [DataRequired()])        

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)