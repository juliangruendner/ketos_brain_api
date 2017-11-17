from rdb.rdb import db


class Environment(db.Model):
    """Environment Class"""

    __tablename__ = "environment"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    jupyter_port = db.Column(db.Integer)
    jupyter_token = db.Column(db.Text)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    authorized_users = db.relationship('User', lazy=True, secondary='user_environment_access')

    def __init__(self):
        super(Environment, self).__init__()

    def __repr__(self):
        """Display when printing a environment object"""

        return "<Name: {}, description: {}>".format(self.name, self.description)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
