from flask import url_for, request, current_app

from app.auth.models import User, PreAllowedUser
from app.extensions import db


def test_register_and_login(client, database):
    # Register unconfirmed user
    response = client.post(url_for('auth.register'), data={
        'email': 'a@a.com',
        'password': 'a',
        'password2': 'a',
    }, follow_redirects=True)
    assert response.status_code == 200
    response_data = response.get_data(as_text=True)
    assert 'mensagem de confirmação' in response_data

    # Login and see unfonfirmed page
    response = client.post(url_for('auth.login'), data={
        'email': 'a@a.com',
        'password': 'a',
    }, follow_redirects=True)
    assert response.status_code == 200
    response_data = response.get_data(as_text=True)
    assert 'Você ainda não confirmou sua conta' in response_data

    # Confirm user account by token
    user = User.query.filter_by(email='a@a.com').first()
    token = user.generate_confirmation_token()
    response = client.get(url_for('auth.confirm', token=token),
                          follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert 'Conta verificada' in response_data

    # TODO: fix this code to consider an authorized and non-authorized user
    # with is needed to access request context
    # with client:
    #     # Log in and redirect user to MAIN_ENDPOINT
    #     response = client.post(url_for('auth.login'), data={
    #         'email': 'a@a.com',
    #         'password': 'a',
    #     }, follow_redirects=True)
    #     assert response.status_code == 200
    #     assert request.path == url_for(current_app.config.get('MAIN_ENDPOINT'))

    #     print(user.role)
    #     # Log out and redirect user to login screen
    #     response = client.get(url_for('auth.logout'),
    #                           follow_redirects=True)
    #     data = response.get_data(as_text=True)
    #     assert response.status_code == 200
    #     assert 'Log Out realizado' in data
    #     assert request.path == '/auth/login'
