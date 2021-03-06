from flask import render_template

from app.errors import bp

from app import db

@bp.app_errorhandler(404)
def not_found_error(error):
    """This renders a 404 page."""
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """
    
    This renders a 500 page and reverts to 
    an earlier version of the db.
    """
    
    db.session.rollback()
    return render_template('errors/500.html'), 500