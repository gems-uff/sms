from flask import Blueprint, render_template

from app.auth.decorators import restrict_to_logged_users


blueprint = Blueprint('main', __name__)
blueprint.before_request(restrict_to_logged_users)

@blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html')
