
import pytest

from config import TestConfig
from app import create_app
from app.extensions import db


@pytest.fixture(scope='function')
def app():
    my_app = create_app(TestConfig)
    app_context = my_app.app_context()
    app_context.push()
    yield my_app
    app_context.pop()


@pytest.fixture(scope='function')
def database(app):
    db.create_all()
    yield database
    db.session.close()
    db.drop_all()


@pytest.fixture(scope='function')
def client(app, database):
    test_client = app.test_client(use_cookies=True)
    yield test_client
