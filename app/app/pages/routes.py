from flask import Blueprint
from flask import render_template
from flask import request, redirect, session


pages = Blueprint('pages', __name__)

@pages.route('/')
def landing():
    return render_template('landing.html')

@pages.route('/login', methods=['GET', 'POST'])
def login_page():
    from app.model import User
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
        user_id = 1
        # add authentication logic


        #fail, do something
        
        # success
        session['user_id'] = 2
        session['logged_in'] = True
        return redirect('/dashboard')

@pages.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        return render_template('dashboard.html')
    else:
        # Not logged in, redirect to login page or send an error message
        return redirect('/login')

@pages.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')
