import os

from flask import Flask

import config
from app.logger import register_logger
from app.extensions import register_extensions
from app.commands import register_commands
from app.blueprints import register_blueprints
from app.admin import register_admin
from app.errors import register_error_handlers


def create_app(config_object=config.Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True

    register_logger(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_admin(app)
    register_error_handlers(app)

    return app
