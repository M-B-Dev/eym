import os

import rq

import logging

from logging.handlers import SMTPHandler, RotatingFileHandler

from redis import Redis

from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from flask_login import LoginManager

from flask_mail import Mail

from flask_jsglue import JSGlue

from flask_babel import Babel, lazy_gettext as _l

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'admin.login'
login.login_message = _l('Please log in to access this page.')
jsglue = JSGlue()
mail = Mail()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('EandM-tasks', connection=app.redis)


    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'auth.login'
    login.login_message = _l('Please log in to access this page.')
    mail.init_app(app)
    babel.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.shop import bp as shop_bp
    app.register_blueprint(shop_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.checkout import bp as checkout_bp
    app.register_blueprint(checkout_bp)

    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='E & M Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/E&M.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('E & M startup')
    
    return app

@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    return "en"

from app import models