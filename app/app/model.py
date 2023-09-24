from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Sequence


class User(db.Model):
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)    
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(255))  # To store the hashed password

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)