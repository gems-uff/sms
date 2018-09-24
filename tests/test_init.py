import os


def test_init_app(app):
    assert app.testing is True
    assert app.debug is False
    assert app.config.get('SQLALCHEMY_DATABASE_URI') == os.environ.get('TEST_DATABASE_URL')
    assert app.config.get('SQLALCHEMY_DATABASE_URI') != os.environ.get('DATABASE_URL')
