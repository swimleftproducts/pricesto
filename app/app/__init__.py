from flask import Flask
from app.basic import basic
from app.pages import pages
from app.api import api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from datetime import timedelta

migrate = Migrate()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] ='secret_for_now'

    #db config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pricesto:AVNS_6pj-pKySki6kw_9O7ec@app-ca6b7a59-46b4-44dc-8c4f-8b4998dfaa3f-do-user-14640571-0.b.db.ondigitalocean.com:25060/pricesto?sslmode=require'



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

