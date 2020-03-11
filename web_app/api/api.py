from flask import current_app

from web_app.api import bp

@bp.route('/', methods=['GET'])
def index():
    return 'Hello'
