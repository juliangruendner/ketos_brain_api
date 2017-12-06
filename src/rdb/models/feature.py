from rdb.rdb import db
import datetime


class Feature(db.Model):
    """Feature Class"""

    __tablename__ = "feature"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    resource = db.Column(db.Text, nullable=False)
    parameter_name = db.Column(db.Text, nullable=False)
    value = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=datetime.datetime.now)
    feature_sets = db.relationship('FeatureSet', lazy=True, secondary='feature_feature_set')

    def __init__(self):
        super(Feature, self).__init__()

    def __repr__(self):
        """Display when printing a feature object"""

        return "<ID: {}, Name: {}, description: {}>".format(self.id, self.name, self.description)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
