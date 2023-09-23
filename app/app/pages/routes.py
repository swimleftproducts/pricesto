from flask import Blueprint
from flask import render_template

pages = Blueprint('pages', __name__)

@pages.route('/')
def landing():
    return render_template('landing.html')