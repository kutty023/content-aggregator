from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from celery import Celery
import os

# initialising the flask  extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config = True)

    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY'),
        SQLAlchemy_DATABASE_URI = os.environ.get('DATABASE_URL'),
        CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL'),
        CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    )

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'

    from . import routes
    app.register_blueprint(routes.bp)

    from . import models

    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)
