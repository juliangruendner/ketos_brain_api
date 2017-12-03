from rdb.rdb import db, LowerCaseText
from enum import Enum
import datetime


class Environment(db.Model):
    """Environment Class"""

    __tablename__ = "environment"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    container_id = db.Column(db.Text, nullable=False)
    container_name = db.Column(db.Text, nullable=False)
    status = db.Column(LowerCaseText, nullable=False)
    jupyter_port = db.Column(db.Text, nullable=False)
    jupyter_token = db.Column(db.Text, nullable=False)
    jupyter_url = None
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # authorized_users = db.relationship('User', lazy='subquery', secondary='user_environment_access')
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    ml_models = db.relationship('MLModel', lazy='select', cascade='delete, delete-orphan', backref='environment')
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=datetime.datetime.now)

    def __init__(self):
        super(Environment, self).__init__()

    def __repr__(self):
        """Display when printing a environment object"""

        return "<ID: {}, Name: {}, description: {}>".format(self.id, self.name, self.description)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def set_jupyter_url(self):
        # TODO: read host address from os
        host = 'localhost'
        self.jupyter_url = host + ':' + self.jupyter_port + '/?token=' + self.jupyter_token

    def hide_jupyter_data(self):
        self.jupyter_port = None
        self.jupyter_token = None
        self.jupyter_url = None

    class Status(Enum):
        running = 'running'
        stopped = 'stopped'
