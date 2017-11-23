from passlib.apps import custom_app_context as pwd_context
from rdb.rdb import db


class User(db.Model):
    """User class"""

    __tablename__ = "user"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.Text, nullable=True)
    last_name = db.Column(db.Text, nullable=True)
    username = db.Column(db.Text, unique=True, index=True, nullable=False)
    email = db.Column(db.Text, unique=True, index=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_images = db.relationship('Image', lazy=True, backref='creator')
    created_environments = db.relationship('Environment', lazy=True, backref='creator')
    created_ml_models = db.relationship('MLModel', lazy=True, backref='creator')
    accessible_evironments = db.relationship('Environment', lazy='subquery', secondary='user_environment_access')
    assigned_groups = db.relationship('UserGroup', lazy='subquery', secondary='user_group_assignment')

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


def get_user_by_username(username):
    # is username the real username or the email
    # username: not @ contained
    # email: @ contained
    username = str(username)
    u = None
    if "@" in username:
        u = User.query.filter_by(email=username.lower()).first()
    else:
        u = User.query.filter_by(username=username.lower()).first()

    return u
