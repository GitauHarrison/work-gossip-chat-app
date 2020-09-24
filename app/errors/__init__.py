from flask import Blueprint

bp = Blueprint('errors', __name__)

import app.errors import handlers