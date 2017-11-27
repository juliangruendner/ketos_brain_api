from rdb.rdb import db, LowerCaseText


class Image(db.Model):
    """Image class"""

    __tablename__ = "image"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(LowerCaseText, unique=True, nullable=False)
    title = db.Column(db.Text)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    environments_based_on_this = db.relationship('Environment', lazy=True, backref='base_image')

    def __init__(self):
        super(Image, self).__init__()

    def __repr__(self):
        """Display when printing a image object"""

        return "<ID: {}, description: {}>".format(self.id, self.desription)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
