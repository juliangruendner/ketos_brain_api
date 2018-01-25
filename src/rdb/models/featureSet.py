from rdb.rdb import db
import datetime
from flask import g
from flask_restful import abort
import rdb.models.feature as Feature
import rdb.models.user as User


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


def create(name, desc, creator_id=None):
    fs = FeatureSet()
    fs.name = name
    fs.description = desc

    if not creator_id:
        fs.creator_id = g.user.id
    else:
        fs.creator_id = creator_id

    db.session.add(fs)
    db.session.commit()
    return fs


def get(feature_set_id, raise_abort=True):
    fs = FeatureSet.query.get(feature_set_id)

    if raise_abort and not fs:
        abort_if_feature_set_doesnt_exist(feature_set_id)

    return fs


def abort_if_feature_set_doesnt_exist(feature_set_id):
    abort(404, message="feature set {} doesn't exist".format(feature_set_id))


def get_all():
    return FeatureSet.query.all()


def get_all_for_user(user_id):
    return FeatureSet.query.filter_by(creator_id=user_id).all()


def remove_features(feature_set_id, feature_ids, raise_abort=True):
    fs = get(feature_set_id, raise_abort=raise_abort)
    for id in feature_ids:
        f = Feature.get(id, raise_abort=raise_abort)
        if f in fs.features:
            fs.features.remove(f)

    db.session.commit()

    return fs


def add_features(feature_set_id, feature_ids, raise_abort=True):
    fs = get(feature_set_id, raise_abort=raise_abort)
    for id in feature_ids:
        f = Feature.get(id, raise_abort=raise_abort)
        if f not in fs.features:
            fs.features.append(f)

    db.session.commit()
    return fs


def update(feature_set_id, name=None, desc=None, raise_abort=True):
    fs = get(feature_set_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(fs.creator_id)

    if name:
        fs.name = name

    if desc:
        fs.description = desc

    db.session.commit()
    return fs, 200


def delete(feature_set_id, raise_abort=True):
    fs = get(feature_set_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(fs.creator_id)

    fs.features = []
    db.session.commit()

    db.session.delete(fs)
    db.session.commit()

    return feature_set_id
