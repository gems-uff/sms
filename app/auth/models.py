from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask import current_app

from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    VIEW = 0x01
    CREATE = 0x02
    EDIT = 0x04
    DELETE = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.VIEW, True),
            'Staff': (Permission.VIEW |
                      Permission.EDIT |
                      Permission.CREATE |
                      Permission.DELETE,
                      False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    stock_mail_alert = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @staticmethod
    def insert_admin():
        admin_email = current_app.config.get('SYSTEM_ADMIN_EMAIL')
        admin_user = User.query.filter_by(email=admin_email).first()
        if admin_user is None:
            admin_user = User(
                email=admin_email,
                password=current_app.config.get('SYSTEM_ADMIN_PASSWORD'),
            )
        admin_user.role = Role.query.filter_by(name='Administrator').first()
        admin_user.confirmed = True
        admin_user.stock_mail_alert = True
        db.session.add(admin_user)
        db.session.commit()

    @classmethod
    def get_stock_alert_emails(cls):
        return [
            u.email for u in User.query.all()
            if u.is_administrator() and u.stock_mail_alert
        ]

    def can(self, permissions: int):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def generate_confirmation_token(self):
        serializer = Serializer(current_app.config['SECRET_KEY'])
        return serializer.dumps({'confirm': self.id})

    def confirm(self, token):
        serializer = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except Exception:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.email



class PreAllowedUser(db.Model):
    """Table storing users that are directly added as 'Staff'"""
    __tablename__ = 'pre_allowed_users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128))
    email = db.Column(db.String(128))

    @classmethod
    def get_emails(cls):
        return [u.email for u in cls.query.all()]
