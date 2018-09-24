from app.main.views import blueprint as main
from app.auth.views import blueprint as auth


def register_blueprints(app):
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
