from rdb.rdb import db, LowerCaseText
import datetime


class MLModel(db.Model):
    """Image class"""

    __tablename__ = "ml_model"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'), nullable=False)
    ml_model_name = db.Column(db.Text, nullable=False)
    name = db.Column(LowerCaseText, nullable=False)
    desription = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=datetime.datetime.now)

    def __init__(self):
        super(MLModel, self).__init__()

    def __repr__(self):
        """Display when printing a image object"""

        return "<ID: {}, name: {}, description: {}>".format(self.id, self.name, self.desription)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
