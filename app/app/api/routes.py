from flask import Blueprint, session

api = Blueprint('api', __name__)

# @api.route('/login', methods=['POST'])
# def login():
#     user = {'id': 1}
#     if user:
#         session['user_id'] = user['id']
#         return 'valid'
#     return "Login failed", 401

# @api.route('/logout')
# def logout():
#     session.clear()
#     return 'logged out'