from rdb.rdb import db
import datetime


class FeatureSet(db.Model):
    """Feature Set Class"""

    __tablename__ = "feature_set"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=datetime.datetime.now)
    features = db.relationship('Feature', lazy='subquery', secondary='feature_feature_set')
    ml_models = db.relationship('MLModel', lazy='select', cascade='delete, delete-orphan', backref='feature_set')

    def __init__(self):
        super(FeatureSet, self).__init__()

    def __repr__(self):
        """Display when printing a feature set object"""

        return "<ID: {}, Name: {}, description: {}>".format(self.id, self.name, self.description)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
