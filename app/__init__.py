from flask import Flask, request
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_babel import Babel
from flask_babel import lazy_gettext as _l

app = Flask(__name__)
app.config.from_object(Config)
boostrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
moment = Moment(app)
babel = Babel(app)

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME' or app.config['MAIL_PASSWORD']]:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@'  + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'][0],
            subject='ChatApp Failure',
            credentials=auth, secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/tinker_app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Tinker ChatApp')

@babel.localeselector
def get_locale():
    #return request.accept_languages.best_match(app.config['LANGUAGES'])
    return 'en'

from app import routes, models, errors