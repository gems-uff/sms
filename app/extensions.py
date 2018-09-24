from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment



db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bootstrap = Bootstrap()
login_manager = LoginManager()
moment = Moment()

def setup_login_manager(manager, app):
    manager.init_app(app)
    manager.session_protection = 'strong'
    manager.login_view = 'auth.login'
    login_manager.login_message = 'Realize login para acessar essa página'


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    setup_login_manager(login_manager, app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
