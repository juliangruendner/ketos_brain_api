from rdb.rdb import db, LowerCaseText


class MLModel(db.Model):
    """Image class"""

    __tablename__ = "ml_model"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'), nullable=False)
    name = db.Column(LowerCaseText, nullable=False)
    desription = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('environment_id', 'name', name='pk_environment_id_ml_model_name'),)

    def __init__(self):
        super(MLModel, self).__init__()

    def __repr__(self):
        """Display when printing a image object"""

        return "<ID: {}, name: {}, description: {}>".format(self.id, self.name, self.desription)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
