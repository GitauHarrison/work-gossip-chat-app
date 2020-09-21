from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
boostrap = Bootstrap(app)
login = LoginManager(app)

from app import routes, models