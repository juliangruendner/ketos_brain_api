from passlib.apps import custom_app_context as pwd_context
from rdb.rdb import db


class User(db.Model):
    """User class"""

    __tablename__ = "User"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.Text, nullable=True)
    last_name = db.Column(db.Text, nullable=True)
    username = db.Column(db.Text, unique=True, index=True, nullable=False)
    email = db.Column(db.Text, unique=True, index=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

    def __init__(self, first_name, last_name, username, email, password):
        super(User, self).__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.hash_password(password)

    def __repr__(self):
        """Display when printing a user object"""

        return "<Name: {} {}, username: {}, e-mail: {}>".format(self.first_name, self.last_name, self.username, self.email)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
