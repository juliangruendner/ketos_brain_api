from rdb.rdb import db


class FeatureFeatureSet(db.Model):
    __tablename__ = 'feature_feature_set'

    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'), primary_key=True)
    feature_set_id = db.Column(db.Integer, db.ForeignKey('feature_set.id'), primary_key=True)
    feature = db.relationship('Feature', backref=db.backref("feature_feature_set_link"))
    feature_set = db.relationship('FeatureSet', backref=db.backref("feature_set_feature_link"))
