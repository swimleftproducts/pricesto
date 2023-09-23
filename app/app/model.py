from app import db

class User(db.Model):
    id = db.Column(db.String(20), primary_key=True, unique = True)
    username = db.Column(db.String(120), unique = True)
