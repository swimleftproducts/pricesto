from flask import Blueprint


basic = Blueprint('basic', __name__)

@basic.route('/health_check')
def health_check():
    return 'healthy'