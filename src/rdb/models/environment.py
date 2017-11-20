from rdb.rdb import db


class Environment(db.Model):
    """Environment Class"""

    __tablename__ = "environment"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    jupyter_port = db.Column(db.Text)
    jupyter_token = db.Column(db.Text)
    jupyter_url = None
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    authorized_users = db.relationship('User', lazy=True, secondary='user_environment_access')
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    ml_models = db.relationship('MLModel', lazy=True, backref='environment')

    def __init__(self):
        super(Environment, self).__init__()

    def __repr__(self):
        """Display when printing a environment object"""

        return "<ID: {}, Name: {}, description: {}>".format(self.id, self.name, self.description)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def fill_jupyter_url(self):
        self.jupyter_url = 'port:' + self.jupyter_port + ', token: ' + self.jupyter_token
