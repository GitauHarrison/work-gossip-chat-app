import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['tastebolder@gmail.com']

    LANGUAGES = ['en', 'sw']

    POSTS_PER_PAGE = 10

    MS_TRANSLATOR_KEY = '344435f010f8410caaa6c1f972507a3e'

    ELASTICSEARCH_URL = 'https://paas:d57302553f5b61953f15085e1bd1ce1c@oin-us-east-1.searchly.com'

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    DATABASE_URL = 'postgres://xazhpuvscwddel:cb83ea3cf2383d9c15cd51086a932c615dc15552b56db1de855bd5ca6f02dd4f@ec2-54-172-173-58.compute-1.amazonaws.com:5432/d839sqtunrhseg'