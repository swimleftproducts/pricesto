from flask import Flask
from app.basic import basic
from app.pages import pages
from app.api import api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from datetime import timedelta
import os


# detect env
MODE = os.environ.get('MODE', 'local')

migrate = Migrate()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')


    db.init_app(app)
    migrate.init_app(app, db)

    #session config
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'
    app.config['SESSION_SQLALCHEMY'] = db 
    Session(app)

    from .model import User 

    app.register_blueprint(basic)
    app.register_blueprint(pages)
    app.register_blueprint(api, url_prefix='/api')

    return app

