'''
Flask-Admin has issues when used with Application Factory pattern.
Since I had issues when using it with pytest, I had to move the admin
instance to "register_admin" method.

https://github.com/flask-admin/flask-admin/issues/910
'''
from flask import redirect, url_for, request
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from app.extensions import db
from app.auth.models import User, Role, PreAllowedUser
from app.main.models import Product, Specification, StockProduct, Stock


class ProtectedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


def register_admin(app):
    admin = Admin(app=app, template_mode='bootstrap3')
    admin.add_link(MenuLink(name='Voltar', url=('/')))
    admin.add_views(
        ProtectedModelView(User, db.session),
        ProtectedModelView(Role, db.session),
        ProtectedModelView(PreAllowedUser, db.session),
        ProtectedModelView(Product, db.session),
        ProtectedModelView(Specification, db.session),
        ProtectedModelView(StockProduct, db.session),
        ProtectedModelView(Stock, db.session),
    )
