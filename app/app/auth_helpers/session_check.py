from flask import request, g
from datetime import datetime
from app.model import UserSession
from app.database import db

def verify_session():
    print('checking session')
    session_id = request.cookies.get('session_id')
    if not session_id:
        g.user = None
        return

    user_session = UserSession.query.filter_by(session_id=session_id).first()
    if not user_session:
        g.user = None
        return

    if not user_session.expiration_time:
        user_session.expiration_time = datetime.utcnow()

    # Check if the session has expired
    if datetime.utcnow() > user_session.expiration_time:
        # Session has expired, remove it from the database
        db.session.delete(user_session)
        db.session.commit()
        g.user = None
        return

    # If everything is fine, set the user object in the g proxy
    print('valid session')
    g.user = user_session.user_id
    g.session_id = session_id
