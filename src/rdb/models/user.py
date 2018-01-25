from passlib.apps import custom_app_context as pwd_context
from rdb.rdb import db, LowerCaseText
import datetime
from flask_restful import abort


class User(db.Model):
    """User class"""

    __tablename__ = "user"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.Text, nullable=True)
    last_name = db.Column(db.Text, nullable=True)
    username = db.Column(LowerCaseText, unique=True, index=True, nullable=False)
    email = db.Column(LowerCaseText, unique=True, index=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_images = db.relationship('Image', lazy=True, backref='creator')
    created_environments = db.relationship('Environment', lazy=True, backref='creator')
    created_ml_models = db.relationship('MLModel', lazy=True, backref='creator')
    created_features = db.relationship('Feature', lazy=True, backref='creator')
    created_feature_sets = db.relationship('FeatureSet', lazy=True, backref='creator')
    # accessible_evironments = db.relationship('Environment', lazy='subquery', secondary='user_environment_access')
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=datetime.datetime.now)

    def __init__(self):
        super(User, self).__init__()

    def __repr__(self):
        """Display when printing a user object"""

        return "<ID: {}, Name: {} {}, username: {}, e-mail: {}>".format(self.id, self.first_name, self.last_name, self.username, self.email)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


def get_by_username(username, raise_abort=True):
    # is username the real username or the email
    # username: not @ contained
    # email: @ contained
    username = str(username)
    u = None
    if "@" in username:
        u = User.query.filter_by(email=username.lower()).first()
    else:
        u = User.query.filter_by(username=username.lower()).first()

    if raise_abort and not u:
        abort_if_user_doesnt_exist(username)

    return u


def abort_if_user_doesnt_exist(user_id):
        abort(404, message="user {} doesn't exist".format(user_id))


def get_user(user_id, raise_abort=True):
    u = User.query.get(user_id)

    if raise_abort and not u:
        abort_if_user_doesnt_exist(user_id)

    return u


def get_all():
    return User.query.all()


def create(username, email, password, first_name=None, last_name=None):
    u = User()
    u.username = username
    u.email = email
    u.hash_password(password)
    u.first_name = first_name
    u.last_name = last_name

    db.session.add(u)
    db.session.commit()

    return u
