from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from rdb.rdb import db


class User(db.Model):
    """User class"""

    __tablename__ = "User"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

    def __init__(self, first_name, last_name, email, password):
        super(User, self).__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hash_password(password)

    def __repr__(self):
        """Display when printing a ToDo object"""

        return "<user: {} {}, e-mail: {}>".format(self.first_name, self.last_name, self.email)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
