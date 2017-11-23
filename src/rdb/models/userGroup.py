from rdb.rdb import db


class UserGroup(db.Model):
    """User Group class"""

    __tablename__ = "user_group"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    description = db.Column(db.Text)
    users_assigned_to = db.relationship('User', lazy='subquery', secondary='user_group_assignment')

    def __init__(self):
        super(UserGroup, self).__init__()

    def __repr__(self):
        """Display when printing a user group object"""

        return "<ID: {}, Name: {}, description: {}>".format(self.id, self.group_name, self.description)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
