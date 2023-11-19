from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Sequence
import datetime


class User(db.Model):
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)    
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(255))  # To store the hashed password

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Assuming you have a user model and this is a foreign key
    session_id = db.Column(db.String(256), unique=True, nullable=False)
    creation_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    expiration_time = db.Column(db.DateTime)

    def __init__(self, user_id, session_id, expiration_time=None):
        self.user_id = user_id
        self.session_id = session_id
        self.expiration_time = expiration_time

    def __repr__(self):
        return f'<UserSession {self.id} for User {self.user_id}>'