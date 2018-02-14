from rdb.rdb import db, LowerCaseText
import datetime
from flask import g
import rdb.models.environment as Environment
import requests
import rdb.models.featureSet as FeatureSet
from flask_restful import abort
import rdb.models.user as User


class MLModel(db.Model):
    """Image class"""

    __tablename__ = "ml_model"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'), nullable=False)
    ml_model_name = db.Column(db.Text, nullable=False)
    name = db.Column(LowerCaseText, nullable=False)
    description = db.Column(db.Text, nullable=True)
    condition_refcode = db.Column(db.Text, nullable=True)
    condition_name = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=datetime.datetime.now)
    feature_set_id = db.Column(db.Integer, db.ForeignKey('feature_set.id'), nullable=True)

    def __init__(self):
        super(MLModel, self).__init__()

    def __repr__(self):
        """Display when printing a image object"""

        return "<ID: {}, name: {}, description: {}>".format(self.id, self.name, self.desription)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def create(name, desc, env_id, feature_set_id, condition_refcode=None, condition_name=None, create_example_model=False, raise_abort=True):
    e = Environment.get(env_id, raise_abort=raise_abort)

    m = MLModel()

    if feature_set_id:
        fs = FeatureSet.get(feature_set_id, raise_abort=raise_abort)
        m.feature_set_id = fs.id

    m.environment_id = e.id
    m.name = name
    m.description = desc
    m.creator_id = g.user.id

    if condition_refcode:
        m.condition_refcode = cond_refcode

    if condition_name:
        m.condition_name = cond_name

    params = None
    if create_example_model:
        params = {'createExampleModel': create_example_model}
    print(create_example_model)
    resp = requests.post('http://' + e.container_name + ':5000/models', params=params).json()
    m.ml_model_name = str(resp['modelName'])

    db.session.add(m)
    db.session.commit()

    return m


def abort_if_model_doesnt_exist(model_id):
        abort(404, message="model {} doesn't exist".format(model_id))


def get(model_id, raise_abort=True):
    m = MLModel.query.get(model_id)

    if raise_abort and not m:
        abort_if_model_doesnt_exist(model_id)

    return m


def get_all():
    return MLModel.query.all()


def get_all_for_user(user_id):
    return MLModel.query.filter_by(creator_id=user_id).all()


def update(model_id, name=None, desc=None, condition_refcode=None, condition_name=None, feature_set_id=None, raise_abort=True):
    m = get(model_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(m.creator_id)

    if name:
        m.name = name

    if desc:
        m.description = desc

    if condition_refcode:
        m.condition_refcode = condition_refcode

    if condition_name:
        m.condition_name = condition_name

    if feature_set_id:
        fs = FeatureSet.get(feature_set_id, raise_abort=raise_abort)
        m.feature_set_id = fs.id

    db.session.commit()
    return m, 200


def delete(model_id, raise_abort=True):
    m = get(model_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(m.creator_id)

    db.session.delete(m)
    db.session.commit()

    return model_id
