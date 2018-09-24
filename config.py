import os

from dotenv import load_dotenv


load_dotenv(override=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Base
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV')

    # Admin credentials
    SYSTEM_ADMIN_EMAIL = os.environ.get('SYSTEM_ADMIN_EMAIL')
    SYSTEM_ADMIN_PASSWORD = os.environ.get('SYSTEM_ADMIN_PASSWORD')

    # Environment (Heroku)
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    # Flask SQLAlchemy
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Flask Mail
    MAIL_DEFAULT_SENDER = 'Unknown Sender'
    MAIL_SENDER = os.environ.get('MAIL_SENDER') or MAIL_DEFAULT_SENDER
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = True

    # Flask Login
    LOGIN_MESSAGE = 'É necessário ralizar login para acessar essa página'

    # Business rules
    MAIN_ENDPOINT = os.environ.get('MAIN_ENDPOINT', 'main.index')


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    FLASK_ENV = 'development'
    ENV = 'development'
    TESTING = True
    DEBUG = False
    SERVER_NAME = 'localhost.testing'
    WTF_CSRF_ENABLED = False
