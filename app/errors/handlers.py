from app import db
from flask import render_template
from app.errors import bp

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html', title = 'Page not found'), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title = 'Internal Error'), 500