from flask import Flask
from app.basic import basic
from app.pages import pages
from app.api import api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_session import Session
from datetime import timedelta
import os
from app.database import db
from app.auth_helpers.session_check import verify_session


# detect env
MODE = os.environ.get('MODE', 'local')

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    
    print('loading secret key')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    print('loading db secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

    db.init_app(app)
    migrate.init_app(app, db)

    #session config
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'
    app.config['SESSION_SQLALCHEMY'] = db 
    # Session(app)

    from .model import User 

    app.register_blueprint(basic)
    app.register_blueprint(pages)
    app.register_blueprint(api, url_prefix='/api')

   
    app.before_request(verify_session)


    return app

