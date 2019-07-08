from rdb.rdb import db
import datetime
from flask import g
from flask_restful import abort
import rdb.models.user as User


class Feature(db.Model):
    """Feature Class"""

    __tablename__ = "feature"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    resource = db.Column(db.Text, nullable=False)
    parameter_name = db.Column(db.Text, nullable=False)
    value = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    output_value_path = db.Column(db.Text, nullable=True)
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


def create(resource, parameter_name, value, name, desc, output_value_path=None, creator_id=None):
    f = Feature()
    f.resource = resource
    f.parameter_name = parameter_name
    f.value = value
    f.name = name
    f.description = desc
    f.output_value_path = output_value_path

    if not creator_id:
        f.creator_id = g.user.id
    else:
        f.creator_id = creator_id

    db.session.add(f)
    db.session.commit()
    return f


def abort_if_feature_doesnt_exist(feature_id):
        abort(404, message="feature {} doesn't exist".format(feature_id))


def get(feature_id, raise_abort=True):
    f = Feature.query.get(feature_id)

    if raise_abort and not f:
        abort_if_feature_doesnt_exist(feature_id)

    return f


def get_all():
    return Feature.query.all()


def get_all_for_user(user_id):
    return Feature.query.filter_by(creator_id=user_id).all()


def get_by_res_par_val(resource, parameter_name, value):
    return Feature.query.filter_by(resource=resource).filter_by(parameter_name=parameter_name).filter_by(value=value).first()


def update(feature_id, resource=None, parameter_name=None, value=None, name=None, output_value_path=None, desc=None, raise_abort=True):
    f = get(feature_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(f.creator_id)

    if resource:
        f.resource = resource

    if parameter_name:
        f.parameter_name = parameter_name

    if value:
        f.value = value

    if name:
        f.name = name

    if desc:
        f.description = desc

    if output_value_path:
        f.output_value_path = output_value_path

    db.session.commit()
    return f


def delete(feature_id, raise_abort=True):
    f = get(feature_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(f.creator_id)

    db.session.delete(f)
    db.session.commit()

    return feature_id
