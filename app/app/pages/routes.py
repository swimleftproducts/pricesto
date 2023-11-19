from flask import Blueprint
from flask import render_template, flash
from flask import request, redirect, g
from flask import make_response
import uuid
from datetime import datetime, timedelta
from app.model import User, UserSession
from app.database import db

pages = Blueprint('pages', __name__)

@pages.route('/')
def landing():

    return render_template('landing.html')

@pages.route('/register',  methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if 'HX-Request' in request.headers:
            return render_template('partials/register_form.html')
        else:
            return render_template('register.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print('registration attempt ', email, ' ', password)
        
        # check unique email
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email exists', 'danger')
            return redirect('/register')

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

@pages.route('/login', methods=['GET', 'POST'])
def login_page():
    print('request', request)
    if request.method == 'GET':
        if 'HX-Request' in request.headers:
            return render_template('partials/login_form.html')
        else:
            return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print('login attempt ', email, ' ', password)
 
        # add authentication logic
        user = User.query.filter_by(email=email).first()
        print(user)
        if user and user.check_password(password):
            print('valid login')

            session_id = str(uuid.uuid4())
            user_session = UserSession(user_id=user.id, session_id=session_id, expiration_time=(datetime.utcnow() + timedelta(minutes=60)))
            db.session.add(user_session)
            db.session.commit()

            resp = make_response(redirect('/dashboard'))
            resp.set_cookie('session_id', session_id)
            return resp
        else:
            flash('Invalid email or password', 'danger')
            return redirect('/register')

@pages.route('/testing')
def testing():
    print("g is", g)
    return ('hi')

@pages.route('/dashboard')
def dashboard():
    if g.user:
        return render_template('dashboard.html')
    else:
        # Not logged in, redirect to login page or send an error message
        return redirect('/login')

@pages.route('/logout')
def logout():
    if not g.user:
        return redirect('/login')
    else:
        # Try to get the session from the database using the session_id from global context
        session_to_remove = UserSession.query.filter_by(session_id=g.session_id).first()
        
        # If we find the session in the database, delete it
        if session_to_remove:
            db.session.delete(session_to_remove)
            db.session.commit()
            #todo: flash('Logged out successfully!', 'success')
            print('deleted session')
            
        # Removing the user info from the global context (though this is not mandatory as `g` is request-scoped and will reset with each request)
        g.user = None
        
        # Redirect to a page (probably login or landing page) after logout
        return redirect('/login')