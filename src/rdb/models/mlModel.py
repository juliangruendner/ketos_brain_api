from rdb.rdb import db


class MLModel(db.Model):
    """Image class"""

    __tablename__ = "ml_model"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=True)
    desription = db.Column(db.Text, nullable=True)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'))

    __table_args__ = (db.UniqueConstraint('environment_id', 'name', name='unique_environment_model_name'),)

    def __init__(self):
        super(MLModel, self).__init__()

    def __repr__(self):
        """Display when printing a image object"""

        return "<ID: {}, name: {}, description: {}>".format(self.id, self.name, self.desription)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
